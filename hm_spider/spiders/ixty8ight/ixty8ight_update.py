#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from scrapy.http import HtmlResponse

from .ixty8ight import A6ixtySpider


class AdidasUpdateSpider(A6ixtySpider):
    name = '6IXTY_updata'
    start_urls = []

    def parse(self, response: HtmlResponse):
        if response.text and '/item/' in response.url:
            self.log_record_before(response)
            yield self.parse_detail_data(response)

    def add_request(self):
        pass
