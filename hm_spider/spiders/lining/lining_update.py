# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.http import HtmlResponse

from .lining import LiningSpider


class LiningUpdateSpider(LiningSpider):
    name = 'lining_update'
    start_urls = []

    def parse(self, response: HtmlResponse):
        if response.text and re.search('goods-\d+.', response.url):
            self.log_record_before(response)
            yield self.parse_detail_data(response)
            for url in self.parse_urls(response):
                yield scrapy.Request(url, callback=self.parse)
