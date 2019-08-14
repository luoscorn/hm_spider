#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# 全异步加载，无法获取到HTML链接，只有api链接, 备注
#
# Created by flytrap
from .bershka import BershkaSpider


class BershkaNewSpider(BershkaSpider):
    name = 'bershka_new'

    start_urls = [
        'https://www.bershka.cn/itxrest/2/catalog/store/44109528/40259531/category/1010250006/product?languageId=-7'
        'https://www.bershka.cn/itxrest/2/catalog/store/44109528/40259531/category/1010250004/product?languageId=-7'
    ]
