#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import re
import scrapy
from scrapy.http import HtmlResponse

from records.models import SpiderRecord
from .hm import HmSpider


class HmUpdateSpider(HmSpider):
    name = 'hm_update'
    allowed_domains = ['www2.hm.com']
    domain_url = 'https://www2.hm.com'
    start_urls = [
        # 'https://www2.hm.com/zh_cn/sale/ladies/view-all.html',
        # 'https://www2.hm.com/zh_cn/sale/shopbyproductdivided/view-all.html',
        # 'https://www2.hm.com/zh_cn/sale/men/view-all.html',
        # 'https://www2.hm.com/zh_cn/sale/home/view-all.html'
    ]

    @staticmethod
    def product_url(response: HtmlResponse):
        count = response.selector.xpath("//h2[@class='load-more-heading']/@data-total").extract_first().strip()
        url = response.url + f'?sort=newProduct&offset=0&page-size={count}'
        return url

    def parse(self, response: HtmlResponse):
        if response.url.endswith('view-all.html'):
            yield scrapy.Request(self.product_url(response))
        if response.text and re.search('productpage.\d+.', response.url):
            self.logger.info(f'parser html: {response.url}')
            SpiderRecord.objects.create(url=response.url, html=response.text)
            yield self.parse_detail_data(response)
