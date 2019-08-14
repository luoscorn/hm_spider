#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import json
import re
import requests
import scrapy
from scrapy.http import HtmlResponse

from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem


class HmSpider(BaseRedisSpider):
    name = 'hm'
    allowed_domains = ['www2.hm.com']
    domain_url = 'https://www2.hm.com'
    start_urls = [
        # 'https://www2.hm.com/zh_cn/index.html'
        # 'https://www2.hm.com/zh_cn/ladies/shop-by-product/view-all.html',
        # 'https://www2.hm.com/zh_cn/divided/shop-by-product/view-all.html',
        # 'https://www2.hm.com/zh_cn/men/shop-by-product/view-all.html',
        # 'https://www2.hm.com/zh_cn/kids/shop-by-product/baby-girls-size-4m-2y.html',
        # 'https://www2.hm.com/zh_cn/kids/shop-by-product/baby-boy-size-4m-2y.html',
        # 'https://www2.hm.com/zh_cn/kids/shop-by-product/girls-size-18m-8y.html',
        # 'https://www2.hm.com/zh_cn/kids/shop-by-product/boys-size-18m-8y.html',
        # 'https://www2.hm.com/zh_cn/kids/shop-by-product/girls-size-8-14y.html',
        # 'https://www2.hm.com/zh_cn/kids/shop-by-product/boys-size-8-14y.html'
        'https://www2.hm.com/zh_cn/ladies/shop-by-product/view-all/_jcr_content/main/productlisting_30ab.display.json?sort=stock&image-size=small&image=model&offset=0&page-size=36',
        'https://www2.hm.com/zh_cn/divided/shop-by-product/view-all/_jcr_content/main/productlisting_45ad.display.json?sort=stock&image-size=small&image=model&offset=0&page-size=36',
        'https://www2.hm.com/zh_cn/men/shop-by-product/view-all/_jcr_content/main/productlisting_fa5b.display.json?sort=stock&image-size=small&image=model&offset=0&page-size=36',
        'https://www2.hm.com/zh_cn/kids/shop-by-product/baby-girls-size-4m-2y/_jcr_content/main/productlisting.display.json?product-type=kids_babygirl_all&sort=stock&image-size=small&image=stillLife&offset=0&page-size=36',
        'https://www2.hm.com/zh_cn/kids/shop-by-product/baby-boy-size-4m-2y/_jcr_content/main/productlisting.display.json?product-type=kids_babyboy_all&sort=stock&image-size=small&image=stillLife&offset=0&page-size=36',
        'https://www2.hm.com/zh_cn/kids/shop-by-product/girls-size-18m-8y/_jcr_content/main/productlisting.display.json?product-type=kids_girl8y_all&sort=stock&image-size=small&image=stillLife&offset=0&page-size=36',
        'https://www2.hm.com/zh_cn/kids/shop-by-product/boys-size-18m-8y/_jcr_content/main/productlisting.display.json?product-type=kids_boy8y_all&sort=stock&image-size=small&image=stillLife&offset=0&page-size=36',
        'https://www2.hm.com/zh_cn/kids/shop-by-product/girls-size-8-14y/_jcr_content/main/productlisting.display.json?product-type=kids_girl14y_all&sort=stock&image-size=small&image=stillLife&offset=0&page-size=36',
        'https://www2.hm.com/zh_cn/kids/shop-by-product/boys-size-8-14y/_jcr_content/main/productlisting.display.json?product-type=kids_boys14y_all&sort=stock&image-size=small&image=model&offset=0&page-size=36'
    ]

    # start_urls = ['https://www2.hm.com/zh_cn/productpage.0707235001.html']
    custom_settings = {"DOWNLOAD_DELAY": 1}

    def parse(self, response: HtmlResponse):
        if response.text and re.search('productpage.\d+.', response.url):
            # self.logger.info(f'parser html: {response.url}')
            self.log_record_before(response)
            yield self.parse_detail_data(response)
        self.logger.info(f'parser url: {response.url}')
        if response.url in self.start_urls:
            for url in self.get_page_urls(response):
                yield scrapy.Request(url, callback=self.parse)
        if 'productlisting' in response.url:
            for url in self.get_detail_urls(response):
                yield scrapy.Request(url,callback=self.parse)

    @staticmethod
    def get_other_style(data):
        other_style = {}
        for k in data:
            if isinstance(data[k], dict):
                other_style[k] = {
                    'color': data[k].get('name'),
                    'img': data[k].get('images')[0].get('thumbnail'),
                    'color_code': data[k].get('colorCode')
                }
        return other_style

    def parse_detail_data(self, response: HtmlResponse):
        tags = []
        category = None
        i = 0
        for tag in response.xpath("//a[@itemprop='item']/span/text()").extract():
            tag_info = {'name': tag, 'href': ''}
            if i == 1:
                category = tag_info
            i += 1
            tags.append(tag_info)
        for tag in response.xpath("//title/text()").extract_first().split():
            name = tag.strip()
            if name in ['-', '|', 'CN']:
                continue
            tags.append({'name': name, 'href': ''})
        try:
            html = response.xpath('//main').get()
        except Exception as e:
            self.logger.exception(e)
            html = response.text
        p = HMProductItem(html=html, source_url=response.url)
        p['tags'] = tags

        p['category'] = {'name': self.get_category(response.url), 'href': ''}
        p['name'] = response.xpath("//h1[@class='primary product-item-headline']/text()").extract_first().strip()

        p['gender'] = self.get_gender(p['name'], p['tags'])
        data = self.parse_product_data(response)
        if not data:
            return
        p['raw_products'] = data
        p['other_style'] = self.get_other_style(data)
        code = data['articleCode']
        p['code'] = code
        p['group_code'] = code[:-3]
        p['img_urls'] = data[code]['images']
        p['size_select'] = data[code]['sizes']
        p['size_valid'] = self.hm_request_size_valid(response.url, code)
        white_price = data[code].get('whitePriceValue', '0')
        p['white_price'] = float(white_price)
        p['price'] = float(data[code].get('redPriceValue', white_price))
        p['desc'] = data[code].get('description', '')
        p['detail'] = {'composition': data[code].get('composition'), 'detailed': data[code].get('detailedDescriptions')}
        return p

    def hm_request_size_valid(self, url, code: [str, list], site='zh_cn'):
        # 'https://www2.hm.com/zh_cn/getAvailability?variants=0707235001'
        codes = code
        if isinstance(code, list):
            codes = ','.join(code)
        response = requests.get(f'{self.domain_url}/{site}/getAvailability', params={'variants': codes}, headers={
            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) \
             Chrome/73.0.3683.103 Safari/537.36",
            'referer': url,
            'content-type': 'application/json'
        })
        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                self.logger.exception(e)

    @classmethod
    def parse_product_data(cls, response: HtmlResponse):
        data = \
            re.findall(r'productArticleDetails = (.*?)</script><script type="text/template" id="fullscreenModalTmpl">',
                       response.text, re.S)
        if data and data[0].strip().endswith(';'):
            s = data[0].strip()[:-1].replace("'", '"')
            for desk in re.findall('isDesktop.*?\n', s):
                desk = desk.strip()
                new_desk = f'''"{desk[:-1].replace('"', "'")}",''' if desk.endswith(
                    ',') else f'''"{desk.replace('"', "'")}"'''
                s = s.replace(desk, new_desk)
            try:
                results = json.loads(s)
                cls.log_record_after(response.url)
                return results
            except json.decoder.JSONDecodeError:
                cls.log_record_after(response.url, info=s, error='json')
                return {}
        cls.log_record_after(response.url, error='json not found')
        return {}

    def get_category_by_url(self, url: str):
        if 'ladies' in url or 'divided' in url:
            return self.WOMAN
        elif 'men' in url:
            return self.MAN
        elif 'kids_babygirl_all' in url:
            return self.FEMALE_BABY
        elif 'kids_babyboy_all' in url:
            return self.MALE_BABY
        elif 'kids_girl8y_all' in url or 'kids_girl14y_all' in url:
            return self.GIRL
        elif 'kids_boy8y_all' in url or 'kids_boys14y_all' in url:
            return self.BOY
        else:
            return self.OTHER

    @staticmethod
    def get_page_urls(response: HtmlResponse):
        data = json.loads(response.text)
        total = data['total']
        offset = 0
        while offset <= total:
            offset += 36
            url = response.url.replace('offset=0', 'offset=' + str(offset))
            yield url

    def get_detail_urls(self, response: HtmlResponse):
        data = json.loads(response.text)
        c_name = self.get_category_by_url(response.url)
        for p in data['products']:
            url = self.domain_url+p['link']+'?tag_category='+c_name
            yield url

    def get_category(self, url: str):
        params = self.get_url_params(url)
        c_name = params.get('tag_category', [])
        if not c_name:
            msg = 'url:' + url + '缺少tag_category参数'
            self.logger.warning(msg)
            self.log_record_after(url, error=msg)
            raise Exception(msg)
        return c_name[0]

