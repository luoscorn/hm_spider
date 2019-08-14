# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import HtmlResponse

from .uniqlo import UniqloSpider


class UniqloNewSpider(UniqloSpider):
    name = 'uniqlo_new'
    start_urls = [
        # 女装
        'https://www.uniqlo.cn/c/1448748959.html',
        # 男装
        'https://www.uniqlo.cn/c/1448748958.html',
        # 童装
        'https://www.uniqlo.cn/c/1448748960.html',
        # 婴儿装
        'https://www.uniqlo.cn/c/1448748961.html'
    ]

    # def parse(self, response: HtmlResponse):
    #     match = re.search(r'productCode=(?P<code>u\d+)', response.url)
    #     if match:
    #         code = match.groupdict().get('code', None)
    #         if code:
    #             self.log_record_before(response)
    #             for p in self.parse_detail_data(response, code):
    #                 yield p
