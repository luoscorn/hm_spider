# -*- coding: utf-8 -*-
import re
from scrapy.http import HtmlResponse

from .uniqlo import UniqloSpider


class UniqloUpdateSpider(UniqloSpider):
    name = 'uniqlo_update'
    start_urls = []

    def parse(self, response: HtmlResponse):
        match = re.search(r'productCode=(?P<code>u\d+)', response.url)
        if match:
            code = match.groupdict().get('code', None)
            if code:
                self.log_record_before(response)
                for p in self.parse_detail_data(response, code):
                    yield p
