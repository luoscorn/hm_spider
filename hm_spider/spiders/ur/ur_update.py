#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from .ur import UrSpider


class UrUpdateSpider(UrSpider):
    name = 'ur_update'
    start_urls = []

    def parse(self, response):
        if response.text and 'product/detail' in response.url:
            yield self.parse_detail_data(response)

    def add_ajax_url(self):
        pass
