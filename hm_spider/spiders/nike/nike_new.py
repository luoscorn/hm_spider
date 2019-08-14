#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from .nike import NikeSpider


class NikeNewSpider(NikeSpider):
    name = 'nike_new'
    start_urls = [
        # 新品
        'https://store.nike.com/html-services/gridwallData?country=CN&lang_locale=zh_CN&gridwallPath=new-mens/meZ7pu',
        'https://store.nike.com/html-services/gridwallData?country=CN&lang_locale=zh_CN&gridwallPath=新品-女子/meZ7pt',
        # 'https://store.nike.com/html-services/gridwallData?country=CN&lang_locale=zh_CN&gridwallPath=new-womens/meZ7pt&pn=3',
        'https://store.nike.com/html-services/gridwallData?country=CN&lang_locale=zh_CN&gridwallPath=new-boys/meZ7pv',
        'https://store.nike.com/html-services/gridwallData?gridwallPath=女孩-新品/meZ7pw&country=CN&lang_locale=zh_CN'
    ]
