# -*- coding: utf-8 -*-
import re

import scrapy
import json
from scrapy.http import HtmlResponse

from hm_spider.spiders.lining.lining import LiningSpider


class LiningNewSpider(LiningSpider):
    name = 'lining_new'
    # start_urls = [
    #     # 新品
    #     'https://store.lining.com/shop/newProductContent-basketball-all-1.html',
    #     'https://store.lining.com/shop/newProductContent-run-all-1.html',
    #     'https://store.lining.com/shop/newProductContent-sports-all-1.html',
    #     'https://store.lining.com/shop/newProductContent-train-all-1.html'
    # ]
    # custom_settings = {
    #     "DOWNLOAD_DELAY": 1
    # }
    #
    # def parse(self, response: HtmlResponse):
    #     if response.text and re.search('goods-\d+.', response.url):
    #         self.log_record_before(response)
    #         yield self.parse_detail_data(response)
    #     if response.text and 'newProductContent' in response.url:
    #         rs = json.loads(response.text)['data']
    #         pl = rs.get('goodsList', [])
    #         for rl in pl:
    #             for p in rl:
    #                 yield scrapy.Request(self.domain_url + p['link'], callback=self.parse)
    #         while int(rs['page_index']) <= int(rs['page_count']):
    #             url = response.url.replace(rs['page_index'], str(int(rs['page_index']) + 1))
    #             yield scrapy.Request(url, callback=self.parse)



