# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem
import re
from .converse import CharkSpider


class CharkupdateSpider(CharkSpider):
    name = 'chark_update'
    allowed_domains = ['www.converse.com.cn']
    domain_url = ['http://www.converse.com.cn/']
    start_urls = [
        'http://www.converse.com.cn/',
        'https://www.converse.com.cn/men/category.htm?iid=tpnvmc0601201501',
        'https://www.converse.com.cn/women/category.htm?iid=tpnvfc0601201502',
        'https://www.converse.com.cn/kids/category.htm?iid=tpnvkc0601201503',
        'https://www.converse.com.cn/sitemap.xml',
        'https://www.converse.com.cn/all_star/764279C222/item.htm']

    rules = (
        Rule(LinkExtractor(allow=r'.*/item.htm'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'.*/detail.htm.*'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'.*/item.htm.*'), callback='parse_item', follow=True),
    )


