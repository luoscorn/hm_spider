#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import requests

from .ur import UrSpider


class UrNewSpider(UrSpider):
    name = 'ur_new'

    def parse(self, response):
        if response.text and 'product/detail' in response.url:
            yield self.parse_detail_data(response)

    def add_ajax_url(self):
        for i in range(1, 50):
            response = requests.get(self.search_url.format(p=i))
            data = response.json().get('data', {})
            page = data.get('pageData')
            if not page:
                break
            self.add_url(page)
