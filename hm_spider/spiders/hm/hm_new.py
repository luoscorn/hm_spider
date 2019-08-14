#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import re
import scrapy
from scrapy.http import HtmlResponse

from hm_spider.spiders.hm.hm import HmSpider
from records.models import SpiderRecord
from .hm_update import HmUpdateSpider


class HmNewSpider(HmSpider):
    name = 'hm_new'
    start_urls = [
        'https://www2.hm.com/zh_cn/ladies/new-arrivals/clothes/_jcr_content/main/productlisting.display.json?sort=stock&image-size=small&image=model&offset=0&page-size=36',
        'https://www2.hm.com/zh_cn/ladies/new-arrivals/shoes-accessories/_jcr_content/main/productlisting.display.json?sort=stock&image-size=small&image=stillLife&offset=0&page-size=36',
        'https://www2.hm.com/zh_cn/divided/new-arrivals/clothes/_jcr_content/main/productlisting_b27d.display.json?sort=stock&image-size=small&image=model&offset=0&page-size=36',
        'https://www2.hm.com/zh_cn/divided/new-arrivals/shoes-accessories/_jcr_content/main/productlisting.display.json?sort=stock&image-size=small&image=stillLife&offset=0&page-size=36',
        'https://www2.hm.com/zh_cn/men/new-arrivals/clothes/_jcr_content/main/productlisting.display.json?sort=stock&image-size=small&image=model&offset=0&page-size=36',
        'https://www2.hm.com/zh_cn/men/new-arrivals/shoes-and-accessories/_jcr_content/main/productlisting.display.json?sort=stock&image-size=small&image=model&offset=0&page-size=36',
    ]
