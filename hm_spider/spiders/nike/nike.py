#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import json
import re
import scrapy
from scrapy.http import HtmlResponse

from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem


class NikeSpider(BaseRedisSpider):
    name = 'nike'
    allowed_domains = ['store.nike.com', 'www.nike.com']
    domain_url = 'https://store.nike.com'
    start_urls = [
        'https://store.nike.com/html-services/gridwallData?country=CN&lang_locale=zh_CN&gridwallPath=boys/7pv&pn=1',
        'https://store.nike.com/html-services/gridwallData?country=CN&lang_locale=zh_CN&gridwallPath=mens/7pu&pn=1',
        'https://store.nike.com/html-services/gridwallData?country=CN&lang_locale=zh_CN&gridwallPath=womens/7pt&pn=1',
        'https://store.nike.com/html-services/gridwallData?country=CN&lang_locale=zh_CN&gridwallPath=girls/7pw&pn=1'
        ]
    # start_urls = ['https://www.nike.com/cn/t/zoom-kd12-ep-%E7%94%B7%E5%AD%90%E7%AF%AE%E7%90%83%E9%9E%8B-2cPLg9']
    custom_settings = {
        "DOWNLOAD_DELAY": 1
    }

    def parse(self, response: HtmlResponse):
        if 'gridwallData' in response.url:
            try:
                data = json.loads(response.text)
            except json.decoder.JSONDecodeError:
                self.logger.info(response.url)
            else:
                page = data.get('nextPageDataService', None)
                if page:
                    ajax_page_url = self.domain_url+page
                    yield scrapy.Request(ajax_page_url, callback=self.parse)
                self.logger.info(f'gridwallData parser url:{response.url}')
                gender = self.get_gender_by_url(response.url)
                category = self.get_category_by_url(response.url)
                for item in data.get('sections')[0]['items']:
                    url = item['pdpUrl']
                    if '?' not in url:
                        url = url+'?tag_gender='+gender+'&tag_category=' + category
                    else:
                        url = url+'&tag_gender='+gender+'&tag_category=' + category
                    yield scrapy.Request(url, callback=self.parse)
        if response.text and '/cn/t/' in response.url:
            self.log_record_before(response)
            self.logger.info(f'parser detail url:{response.url}')
            items = self.parse_detail_data(response)
            if items:
                for item in items:
                    yield item

    @staticmethod
    def get_images(nodes: list):
        images = []
        for node in nodes:
            properties = node.get('properties', {})
            images.append({
                'thumbnail': properties.get('portraitURL', ''),
                'fullscreen': properties.get('squarishURL', ''),
            })
        return images

    @staticmethod
    def get_size_data(sizes: list):
        for size in sizes:
            size['name'] = ' '.join([size['localizedSize'], size['localizedSizePrefix']])
            size['sizeCode'] = size['skuId']
        return sizes

    @staticmethod
    def get_valid_size_data(sizes: list):
        availability = []
        for size in sizes:
            availability.append(size['skuId'])
        return {'availability': availability, 'raw_data': sizes}

    def parse_detail_data(self, response: HtmlResponse):
        data = re.findall(r'window.INITIAL_REDUX_STATE=(.*?);</script>', response.text, re.S)
        if data and data[0]:
            try:
                product_data = json.loads(data[0])
                self.log_record_after(response.url)
            except json.decoder.JSONDecodeError:
                self.log_record_after(response.url, info=data[0], error='json')
                return
            products = product_data.get('Threads', {}).get('products', {})
            other_style = {k: {
                'color': v.get('colorDescription'),
                'img': v.get('firstImageUrl'),
                'color_code': k.split('-')[-1]
            } for k, v in products.items()}
            items = []
            for k, v in products.items():
                p = HMProductItem(html=response.text.encode('utf8', 'ignore'), source_url=response.url)
                p['name'] = v.get('fullTitle', '')
                p['code'] = k
                p['group_code'] = v.get('styleCode', '')
                p['raw_products'] = v
                p['other_style'] = other_style
                p['category'] = {'name': self.get_category(response.url), 'href': ''}
                p['gender'] = self.get_gender(v.get('fullTitle', ''), [], response.url)

                p['img_urls'] = self.get_images(v['nodes'][0]['nodes'])
                p['size_select'] = self.get_size_data(v['skus'])
                p['size_valid'] = self.get_valid_size_data(v['availableSkus'])

                white_price = v.get('fullPrice', 0)
                p['white_price'] = float(white_price)
                p['price'] = float(v.get('currentPrice', white_price))

                p['desc'] = v.get('descriptionPreview', '')
                p['detail'] = {'composition': '', 'detailed': v['description']}
                items.append(p)
            return items

    @staticmethod
    def get_gender_by_url(url: str):
        if 'men'in url or 'boy' in url or '男' in url:
            return 'male'
        elif 'women' in url or 'girl' in url or '女' in url:
            return 'female'
        else:
            return 'other'

    def get_category_by_url(self, url: str):
        if 'boy' in url or '男孩' in url:
            return self.BOY
        elif 'men'in url or '男' in url:
            return self.MAN
        elif 'girl' in url or '女孩' in url:
            return self.GIRL
        elif 'women' in url or '女' in url:
            return self.WOMAN
        else:
            return self.OTHER

    def get_category(self, url: str):
        params = self.get_url_params(url)
        c_name = params.get('tag_category', [])
        if not c_name:
            msg = 'url:'+url+'缺少tag_category参数'
            self.logger.warning(msg)
            self.log_record_after(url, error=msg)
            raise Exception(msg)
        return c_name[0]

    def get_gender(self, name, tags: [[str], [dict]] = None, url: str = None):
        params = self.get_url_params(url)
        gender = params.get('tag_gender', [])[0]
        if gender and (gender == 'male' or gender == 'female'):
            return gender
        else:
            return BaseRedisSpider.get_gender(name, tags)

