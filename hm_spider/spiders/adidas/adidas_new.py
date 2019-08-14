#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import scrapy
from scrapy.http import HtmlResponse

from .adidas import AdidasSpider


class AdidasNewSpider(AdidasSpider):
    name = 'adidas_new'
    start_urls = [
        # 新品
        'https://www.adidas.com.cn/men_newarrivals',
        'https://www.adidas.com.cn/women_newarrivals',
        'https://www.adidas.com.cn/kids_newarrivals',
    ]

    def parse(self, response: HtmlResponse):
        if response.text and '/item/' in response.url:
            self.log_record_before(response)
            yield self.parse_detail_data(response)
        if 'plp/waterfall.json' in response.url or 'plp/list.json' in response.url:
            items = self.get_product_items(response)
            for item in items:
                code = item.get('c', '')
                if code:
                    yield scrapy.Request(url=self.product_url.format(code=code), callback=self.parse)
