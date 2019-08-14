#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import scrapy
from scrapy.http import HtmlResponse

from .ixty8ight import A6ixtySpider


class A6ixtyNewSpider(A6ixtySpider):
    name = '6IXTY_new'
    allowed_domains = ['www.6ixty8ight.cn']
    start_urls = ['https://www.6ixty8ight.cn/new-arrivals.html?p=']

    def parse(self, response: HtmlResponse):
        if '/new-arrivals/' in response.url:
            yield self.parse_detail_data(response)
        for new_url in response.xpath('//*[@id]/div/div/div/div/div[2]/div/a/@href').extract():
            yield scrapy.Request(new_url, callback=self.parse)