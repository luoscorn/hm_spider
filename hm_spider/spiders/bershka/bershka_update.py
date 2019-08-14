#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# 全异步加载，无法获取到HTML链接，只有api链接, 备注
#
# Created by flytrap
import re
from scrapy.http import HtmlResponse

from .bershka import BershkaSpider


class BershkaUpdateSpider(BershkaSpider):
    name = 'bershka_update'

    start_urls = []

    def parse(self, response: HtmlResponse):
        if re.search(r'category/0/product/\d+?/detail', response.url):
            for p in self.parse_detail_data(response):
                yield p
