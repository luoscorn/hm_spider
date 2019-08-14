#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import json
import scrapy
from scrapy.http import HtmlResponse

from .nike import NikeSpider


class NikeUpdateSpider(NikeSpider):
    name = 'nike_update'
    start_urls = [
        # 降价
        # 'https://store.nike.com/html-services/gridwallData?country=CN&lang_locale=zh_CN&gridwallPath=mens-sale/47Z7pu',
        # 'https://store.nike.com/html-services/gridwallData?gridwallPath=womens-sale%2F47Z7pt&country=CN&lang_locale=zh_CN',
        # 'https://store.nike.com/html-services/gridwallData?gridwallPath=kids-sale%2F47Z1me&country=CN&lang_locale=zh_CN',
    ]

    def parse(self, response: HtmlResponse):
        if response.text and '/cn/t/' in response.url:
            self.log_record_before(response)
            items = self.parse_detail_data(response)
            if items:
                for item in items:
                    yield item
