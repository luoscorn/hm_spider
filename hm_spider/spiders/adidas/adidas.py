#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import json
import scrapy
from scrapy.http import HtmlResponse

from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem


class AdidasSpider(BaseRedisSpider):
    name = 'adidas'
    allowed_domains = ['www.adidas.com.cn']
    domain_url = 'https://www.adidas.com.cn/'
    start_urls = ['https://www.adidas.com.cn/']
    # start_urls = ['https://www.adidas.com.cn/item/DB3245']
    product_url = 'https://www.adidas.com.cn/item/{code}?locale=zh_CN'
    custom_settings = {
        "DOWNLOAD_DELAY": 1
    }

    def parse(self, response: HtmlResponse):
        if response.text and '/item/' in response.url:
            yield self.parse_detail_data(response)
        if 'plp/waterfall.json' in response.url or 'plp/list.json' in response.url:
            items = self.get_product_items(response)
            for item in items:
                code = item.get('c', '')
                if code:
                    yield scrapy.Request(url=self.product_url.format(code=code), callback=self.parse)
        self.logger.info(f'parser url: {response.url}')
        for url in response.selector.xpath(
                '//*[@id]/section/article[4]/div/div[4]/div/div[2]/div/div/div/div[1]/a/@href').extract():
            url = url.strip('/').strip()
            if 'javascript' in url or url.startswith('#'):
                continue
            if not url.startswith('http'):
                url = self.domain_url + url
            if not url.startswith(self.domain_url):
                continue
            yield scrapy.Request(url, callback=self.parse)

    @staticmethod
    def get_product_items(response):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            return []
        else:
            return data.get('returnObject', {}).get('view', {}).get('items', [])

    def add_request(self):
        ni_ci = [[10, 2], [67, 58], [118, 109], [60, 52], [61, 52], [62, 52], [63, 52], [64, 52], [65, 52], [66, 52],
                 [97, 52], [68, 52], [69, 52], [70, 52],
                 [71, 52], [72, 52], [92, 52], [95, 52], [96, 52], [97, 52], [98, 52], [99, 52]]
        for page in range(1, 20):
            for ni, ci in ni_ci:
                url = f'{self.domain_url}plp/waterfall.json?ni={ni}&pn=1&cp={page}&ci={ci}'
                self.server.lpush(self.redis_key, url)

    def setup_redis(self, crawler=None):
        super(AdidasSpider, self).setup_redis(crawler)
        self.add_request()

    @staticmethod
    def get_images(response):
        sels = response.xpath('//li[@class="li-img"]//img')
        images = []
        for sel in sels:
            images.append({
                'thumbnail': sel.attrib['data-lasysrc'],
                'fullscreen': sel.attrib['data-smartzoom'],
            })
        return images

    @staticmethod
    def get_size_data(response):
        sels = response.xpath('//div[@class="overview product-size"]/ul/li')
        sizes = []
        availability = []
        for sel in sels:
            sizes.append({
                'name': sel.attrib['size'],
                'sizeCode': sel.attrib['ipi'],
                'dispalysize': sel.attrib['dispalysize']
            })
            if sel.attrib.get('class', '') != 'is-disabled':
                availability.append(sel.attrib['ipi'])
        return sizes, {'availability': availability}

    def get_category_by_url(self, cate: str):
        if '男孩' in cate or '男童' in cate:
            return self.BOY
        elif '男士' in cate or '男子' in cate:
            return self.MAN
        elif '女童' in cate or '女孩' in cate:
            return self.GIRL
        elif '女子' in cate or '女士' in cate:
            return self.WOMAN
        elif '婴童' in cate and '男童' in cate:
            return self.MALE_BABY
        elif '婴童' in cate and '女童' in cate:
            return self.FEMALE_BABY
        else:
            return self.OTHER

    def parse_detail_data(self, response: HtmlResponse):
        inputs = response.xpath('//div[@class="row float-clearfix"]')
        p = HMProductItem(html=response.text.encode('utf8', 'ignore'), source_url=response.url)
        title_select = response.selector.xpath('//div[@class="pdp-title none-sm"]')
        cate = response.xpath('/html/head/title').extract_first()
        # if tags and tags[0]:
        p['category'] = {'name': self.get_category_by_url(cate), 'href': ''}  # {'name': tags[0], 'href': ''}
        if title_select:
            title_select.xpath('div[@class="goods-tit"]')
            tags = title_select.xpath('div[@class="goods-tit"]/text()').extract_first().strip().split()
            p['tags'] = [{'name': tag, 'href': ''} for tag in tags if tag]
            p['name'] = inputs.xpath('input[@id="itemTitle"]/@value').extract_first()
            p['gender'] = self.get_gender(p['name'], p['tags'])
            p['code'] = inputs.xpath('input[@id="itemCode"]/@value').extract_first()
            p['group_code'] = inputs.xpath('input[@id="itemStyle"]/@value').extract_first()
            p['other_style'] = {
                li.attrib['code']: {'color': '', 'color_code': li.attrib['itemstyle'],
                                    'img': li.xpath('a/img/@src').extract_first()} for li in
                response.xpath('//ul[@id="itemColor"]/li')}
            p['raw_products'] = {}

            p['img_urls'] = self.get_images(response)
            p['size_select'], p['size_valid'] = self.get_size_data(response)

            p['white_price'] = float(inputs.xpath('input[@id="listPrice"]/@value').extract_first())
            p['price'] = float(inputs.xpath('input[@id="salePrice"]/@value').extract_first())

            p['desc'] = response.xpath(
                '//div[@class="large-box1"]/div/div[@class="float-left"]/p/text()').extract_first()
            p['detail'] = {'composition': '', 'detailed': response.xpath('//div[@class="large-box1"]').extract_first()}

            return p
