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


class ZaraSpider(BaseRedisSpider):
    name = 'zara'
    allowed_domains = ['www.zara.cn']
    domain_url = 'https://www.zara.cn/'
    start_urls = ['https://www.zara.cn/cn/']
    # start_urls = ['https://www.zara.cn/cn/zh/抽象印花衬衫-p04406337.html']

    proxies = ['https://47.99.52.225:8888']
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "DOWNLOADER_MIDDLEWARES": {
            'hm_spider.middlewares.ProxyMiddleware': 400,
        }
    }

    def parse(self, response: HtmlResponse):
        if response.text and re.search('-p(\d{8}).html', response.url):
            self.logger.info(f'parser html: {response.url}')
            self.log_record_before(response)
            yield self.parse_detail_data(response)
        self.logger.info(f'parser url: {response.url}')
        if response.url in self.start_urls:
            for url in set(response.xpath("//nav[@class='menu']//a/@href").extract()):
                yield scrapy.Request(url, callback=self.parse)
        for url in set(response.xpath("//ul[@class='product-list _productList  ']/li/a/@href").extract()):
            new_url = self.check_url(url)
            if not new_url:
                continue
            if new_url.startswith('https://www.zara.cn/cn/en'):
                continue
            yield scrapy.Request(new_url, callback=self.parse)

    @staticmethod
    def get_images(response):
        sels = response.xpath('//a[@class="_seoImg main-image"]')
        images = []
        for sel in sels:
            images.append({
                'thumbnail': sel.xpath('@href').extract_first(),
                'fullscreen': sel.xpath('@href').extract_first(),
                'zoom': sel.xpath('img/@src').extract_first(),
            })
        return images

    @staticmethod
    def get_size_data(response):
        sels = response.xpath('//div[@class="size-list"]/label[@class="product-size _product-size "]')
        sizes = []
        availability = []
        for sel in sels:
            sizes.append({
                'name': sel.xpath('span[@class="size-name"]/@title').extract_first(),
                'sizeCode': sel.attrib['for'],
                'data-sku': sel.attrib['data-sku']
            })
            availability.append(sel.attrib['for'])
        return sizes, {'availability': availability}

    def get_category_by_url(self, cate: str):
        if '男孩' in cate or '男童' in cate:
            return self.BOY
        elif '男子' in cate or '男士' in cate:
            return self.MAN
        elif '女童' in cate or '女孩' in cate:
            return self.GIRL
        elif '女士' in cate or '女子' in cate:
            return self.WOMAN
        elif '男婴' in cate:
            return self.MALE_BABY
        elif '女婴' in cate:
            return self.FEMALE_BABY
        else:
            return self.OTHER

    def parse_detail_data(self, response: HtmlResponse):
        p = HMProductItem(html=response.text.encode('utf8', 'ignore'), source_url=response.url)
        code = re.findall(r'p(\d+).html', response.url)
        if code:
            tags = response.xpath('//a[@aria-expanded="true"]/span/text()').extract()
            p['tags'] = [{'name': tag, 'href': ''} for tag in tags if tag]
            p['name'] = response.xpath('//h1[@class="product-name"]/text()').extract_first()
            p['code'] = code[0]
            p['gender'] = self.get_gender(p['name'], p['tags'])
            p['group_code'] = code[0][:5]
            # if tags and tags[0]:
            cate = response.xpath('//*[@id]/head/title').extract_first()
            p['category'] = {'name': self.get_category_by_url(cate), 'href': ''}
            p['img_urls'] = self.get_images(response)
            p['size_select'], p['size_valid'] = self.get_size_data(response)
            p['raw_products'] = {}
            price = re.findall(r'"price":(\d+?),', response.text)[0]
            p['white_price'] = p['price'] = float(f'{price[:-2]}.{price[-2:]}')
            white_price = re.findall(r'"oldPrice":(\d+?),', response.text)
            if white_price:
                p['white_price'] = float(f'{white_price[0][:-2]}.{white_price[0][-2:]}')
            p['desc'] = response.xpath('//div[@id="description"]/p[@class="description"]/text()').extract_first()
            p['detail'] = {'detailed': response.xpath('//div[@id="description"]').extract_first()}
            detail = re.findall('"detailedComposition":(.*?),"categories"', response.text, re.S)
            try:
                data = json.loads(detail[0])
                p['detail']['composition'] = data.get('parts', {})[0].get('components', [])
                self.log_record_after(response.url)
            except json.JSONDecodeError:
                self.log_record_after(response.url, info=detail[0], error='json')

            return p
