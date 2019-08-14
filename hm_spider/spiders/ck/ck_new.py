# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem
import re
from .ck import CkSpider


class CkNewSpider(CkSpider):
    name = 'ck_new'
    allowed_domains = ['www.calvinklein.cn']
    domain_url = ['http://www.calvinklein.cn/']
    start_urls = ['http://www.calvinklein.cn/',
                  'https://www.calvinklein.cn/sitemap.xml',
                  'https://www.calvinklein.cn/category/list?tg=newarrival&g=men&pid=1-2#top',
                  'https://www.calvinklein.cn/category/list?tg=newarrival&g=women&pid=1-13#top',
                  'https://www.calvinklein.cn/category/list?f=26-47&tg=newarrival&pid=1-206#top',
                  'https://www.calvinklein.cn/category/list?t=ckjas&tg=newarrival&pid=1-26#top',
                  'https://www.calvinklein.cn/category/list?c=ckj&tg=newarrival&g=women&id=37-40#top',
                  'https://www.calvinklein.cn/category/list?c=cku&tg=newarrival&g=women&id=69-72#top',
                  'https://www.calvinklein.cn/category/list?c=ckp&tg=newarrival&g=women&id=92-95#top',
                  'https://www.calvinklein.cn/category/list?c=ckja&tg=newarrival&g=women&id=114-117#top',
                  'https://www.calvinklein.cn/category/list?c=ckck&tg=newarrival&g=men&id=171-173#top',
                  'https://www.calvinklein.cn/category/list?c=ckck&tg=newarrival&g=women&id=171-174#top'
                  ]

    rules = (
        Rule(LinkExtractor(allow=r'https://www.calvinklein.cn/item/.*'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'/item/.*'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'.*/item/.*'), callback='parse_item', follow=True),
    )
