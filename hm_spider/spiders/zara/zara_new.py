#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import re
import scrapy
from scrapy.http import HtmlResponse

from .zara_update import ZaraSpider


class ZaraNewSpider(ZaraSpider):
    name = 'zara_new'
    start_urls = [
        # 新品
        'https://www.zara.cn/cn/zh/woman-new-in-l1180.html',
        'https://www.zara.cn/cn/zh/trf-new-in-l941.html',
        'https://www.zara.cn/cn/zh/man-new-in-l711.html'
    ]

    def parse(self, response: HtmlResponse):
        if response.text and re.search('-p(\d{8}).html', response.url):
            self.log_record_before(response)
            yield self.parse_detail_data(response)

        for url in set(response.xpath("//ul[@class='product-list _productList  ']/li/a/@href").extract()):
            new_url = self.check_url(url)
            if not new_url:
                continue
            yield scrapy.Request(new_url, callback=self.parse)
