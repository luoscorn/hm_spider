#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# 全异步加载，无法获取到HTML链接，只有api链接, 备注
#
# Created by flytrap
import json
import re
import scrapy
from scrapy.http import HtmlResponse

from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem


class BershkaSpider(BaseRedisSpider):
    name = 'bershka'
    allowed_domains = ['www.bershka.cn']
    domain_url = 'https://www.bershka.cn/'

    start_urls = ['https://www.bershka.cn/itxrest/2/catalog/store/44109528/40259531/category']

    list_url = 'https://www.bershka.cn/itxrest/2/catalog/store/44109528/40259531/category/{id}/product?languageId=-7'
    detail_url = 'https://www.bershka.cn/itxrest/2/catalog/store/44109528/40259531/category/0/product/{id}/detail'

    proxies = ['https://47.99.52.225:8888']
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "DOWNLOADER_MIDDLEWARES": {
            'hm_spider.middlewares.ProxyMiddleware': 400,
        }
    }

    def parse(self, response: HtmlResponse):
        self.logger.info(f'parser url: {response.url}')
        if response.url.endswith('category'):
            try:
                data = json.loads(response.text)
            except json.JSONDecodeError:
                self.logger.error(f'parser url: {response.url} error')
            else:
                for category in data['categories']:
                    for subcategory in category['subcategories']:
                        yield scrapy.Request(self.list_url.format(id=subcategory['viewCategoryId']), self.parse)
        elif re.search(r'44109528/40259531/category/\d+?/product\?', response.url):
            try:
                data = json.loads(response.text)
            except json.JSONDecodeError:
                self.logger.error(f'parser url: {response.url} error')
            else:
                for product in data['products']:
                    yield scrapy.Request(self.detail_url.format(id=product['id']), self.parse)
        elif re.search(r'category/0/product/\d+?/detail', response.url):
            for p in self.parse_detail_data(response):
                yield p

    @classmethod
    def get_images(cls, img_data, color_id):
        url = 'https://static.bershka.net/4/photos2'
        images = []
        for img in img_data:
            img_path = img['path']
            if img_path.endswith('/'):
                img_path = img_path[:-1]
            if img_path.endswith(color_id):
                for item in img['xmediaItems']:
                    for media in item['medias']:
                        images.append({
                            'thumbnail': f"{url}{img_path}/{media['idMedia']}5.jpg",
                            'fullscreen': f"{url}{img_path}/{media['idMedia']}1.jpg"})

        return images

    @staticmethod
    def get_size_data(sizes: list):
        availability = []
        results = []
        for size in sizes:
            results.append({
                'name': size['name'],
                'sizeCode': size['sku'],
                'position': size['position']
            })
            if size['isBuyable']:
                availability.append(size['sku'])
        return results, {'availability': availability}

    def parse_detail_data(self, response: HtmlResponse):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f'parser url: {response.url} error')
            return
        for product in data['bundleProductSummaries']:
            detail = product['detail']
            tags = [{'name': item['value'] or item['name'], 'href': ''} for item in data['attributes']]
            other_style = [{
                'img': f'https://static.bershka.net/4/photos2{s["image"]["url"]}_3_1_5.jpg',
                'color_code': '',
                'color': s['name']} for s in detail['colors']]
            b = str(data)
            c = re.search(r'女', b)
            if c == 'null':
                category = {'name': self.MAN, 'href': ''}
            else:
                category = {'name': self.WOMAN, 'href': ''}
            for color in detail['colors']:
                sizes = color['sizes']
                price_str = sizes[0]['price']
                old_price = sizes[0]['oldPrice']
                white_price = price = float(f'{price_str[:-2]}.{price_str[-2:]}')
                if old_price:
                    white_price = float(f'{old_price[:-2]}.{old_price[-2:]}')
                p = HMProductItem(
                    html='',
                    source_url=response.url,
                    name=data['name'],
                    code=f'{data["id"]}-{color["id"]}',
                    group_code=data['id'],
                    raw_products=data,
                    white_price=white_price,
                    other_style=other_style,
                    price=price, tags=tags, category=category,
                )
                p['gender'] = self.get_gender(data['name'], tags + [category])
                p['img_urls'] = self.get_images(detail['xmedia'], color['id'])

                p['size_select'], p['size_valid'] = self.get_size_data(color['sizes'])
                p['desc'] = detail['description'] or detail['longDescription']
                p['detail'] = {'composition': detail['composition'], 'detailed': ''}
                yield p
