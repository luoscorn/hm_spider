import re

import scrapy
from scrapy.http import HtmlResponse

from hm_spider.spiders.canda.canda import CandaSpider


class CandaNewSpider(CandaSpider):
    name = 'canda_new'
    allowed_domains = ['www.canda.cn']
    domain_url = 'http://www.canda.cn'
    start_urls = [
        'http://www.canda.cn/new-arrival/women.html',
        'http://www.canda.cn/new-arrival/men.html',
        'http://www.canda.cn/new-arrival/boys.html',
        'http://www.canda.cn/new-arrival/girls.html',
        'http://www.canda.cn/new-arrival/male-baby.html',
        'http://www.canda.cn/new-arrival/female-baby.html',
        'http://www.canda.cn/new-arrival/women-acc.html',
        'http://www.canda.cn/new-arrival/men-acc.html'
    ]

