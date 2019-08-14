#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import re
import time
import requests
import scrapy
from scrapy.http import HtmlResponse

from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem


class UrSpider(BaseRedisSpider):
    name = 'ur'
    allowed_domains = ['www.ur.cn']
    domain_url = 'http://www.ur.cn'
    start_urls = ['http://www.ur.cn/index.html']

    # start_urls = ['http://www.ur.cn/product/detail/ff808081667ca8aa016686295974743b.html']
    search_url = 'http://www.ur.cn/product/search/data?pageIndex={p}&categoryId=&categoryNames='
    detail_url = 'http://www.ur.cn/product/detail/{code}.html'
    custom_settings = {"DOWNLOAD_DELAY": 1}

    def parse(self, response: HtmlResponse):
        if response.text and 'product/detail' in response.url:
            self.logger.info(f'parser html: {response.url}')
            yield self.parse_detail_data(response)
        self.logger.info(f'parser url: {response.url}')

    def setup_redis(self, crawler=None):
        super(UrSpider, self).setup_redis(crawler)
        self.add_ajax_url()

    def add_url(self, page_data: list):
        for item in page_data:
            code = item.get('id')
            if code:
                self.server.lpush(self.redis_key, self.detail_url.format(code=code))

    def add_ajax_url(self):
        response = requests.get(self.search_url.format(p=1))
        data = response.json().get('data', {})
        self.add_url(data.get('pageData'))
        for i in range(2, data.get('pageTotal')):
            time.sleep(0.1)  # 防反扒
            response = requests.get(self.search_url.format(p=i))
            data = response.json().get('data', {})
            page = data.get('pageData')
            if not page:
                break
            self.add_url(page)

    @staticmethod
    def get_detail_data(code):
        url = f'http://www.ur.cn/product/detail/init?id={code}'
        response = requests.get(url)
        return response.json()

    @staticmethod
    def get_other_style(response: HtmlResponse):
        other_style = {}
        for a in response.xpath('p/a'):
            code = a.xpath('@data-product-color-id').extract_first()
            other_style[code] = {
                'color': a.xpath('@title').extract_first(),
                'img': a.xpath('img/@src').extract_first(),
                'color_code': a.xpath('@data-id').extract_first()
            }
        return other_style

    @staticmethod
    def get_img_urls(response: HtmlResponse):
        results = []
        for img in response.xpath('//div[@class="detail-row-minPIC"]//img/@src').extract():
            results.append({'thumbnail': img, 'fullscreen': img})
        for img in response.xpath('//div[@class="detail-row-maxPIC"]//img/@src').extract():
            results.append({'thumbnail': img, 'fullscreen': img})
        return results

    @staticmethod
    def get_size_data(response: HtmlResponse, color_code):
        sizes = []
        availability = []
        for a in response.xpath('div/a'):
            if a.xpath('@data-colorid').extract_first() == color_code:
                code = a.xpath('@data-id').extract_first()
                sizes.append({
                    'name': a.xpath('text()').extract_first(),
                    'sizeCode': code
                })
                if 'noquntity' not in a.attrib['class']:
                    availability.append(code)
        return sizes, {'availability': availability}

    def get_category(self, cate: str):
        if 'M' in cate:
            return self.MAN
        if 'W' in cate or 'Y' in cate:
            return self.WOMAN
        else:
            return self.OTHER

    def parse_detail_data(self, response: HtmlResponse):
        items = response.xpath('//div[@class="detail-row-r"]/div[@class="detail-list"]')
        p = HMProductItem(html=response.text.encode('utf8', 'ignore'), source_url=response.url)
        cate = response.xpath('/html/head/title').extract_first()
        p['category'] = {'name': self.get_category(cate), 'href': ''}
        p['name'] = items.xpath('h5/text()').extract_first().strip()
        p['code'] = re.findall(r'product/detail/(\S+).html', response.url)[0]
        p['group_code'] = items[0].xpath('p/text()').extract_first().split('：')[-1]
        p['desc'] = items[1].xpath('p/text()').extract_first()
        p['detail'] = {'composition': items[2].xpath('p/text()').extract_first(), 'detailed': ''}
        p['raw_products'] = {}
        price = items[3].xpath('h1/text()').extract_first()
        if price:
            white_price = items[3].xpath('h3/del/text()').extract_first()
        else:
            white_price = items[3].xpath('h3/text()').extract_first()
            price = white_price
        p['price'] = float(re.search(r'\d+', price).group())
        p['white_price'] = float(re.search(r'\d+', white_price).group())
        p['img_urls'] = self.get_img_urls(response)
        p['other_style'] = self.get_other_style(items[4])
        p['size_select'], p['size_valid'] = self.get_size_data(items[5], p['other_style'][p['code']]['color_code'])

        p['gender'] = self.get_gender(p['name'])
        return p
