# -*- coding: utf-8 -*-
import scrapy
import json
import scrapy
from scrapy.http import HtmlResponse
import re
from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem
from .fiveplus import Fpspider

# 只爬新品行列 可另外追加url
class FpNewspider(Fpspider):
    name = 'fp_new'
    allowed_domains = ['www.fiveplus.com']
    start_urls = ['http://www.fiveplus.com/New_In/list-1-36-inventory%20desc-0-0-0-0-0.shtml']

    def parse(self, response: HtmlResponse):
        if '/product/' in response.url:
            yield self.parse_detail_data(response)
        for url in response.xpath("//div[@class = 'chanpin-bar']/div/div/p[1]/a/@href").extract():
            new_url = 'http://www.fiveplus.com' + url
            yield scrapy.Request(new_url, callback=self.parse)

