#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import re
from .zara import ZaraSpider


class ZaraUpdateSpider(ZaraSpider):
    name = 'zara_update'
    start_urls = [
        # 降价
        # 'https://www.zara.cn/cn/zh/woman-special-prices-l1314.html',
        # 'https://www.zara.cn/cn/zh/man-special-prices-l806.html?v1=1181019'
    ]

    def parse(self, response):
        if response.text and re.search('-p(\d{8}).html', response.url):
            self.log_record_before(response)
            yield self.parse_detail_data(response)
