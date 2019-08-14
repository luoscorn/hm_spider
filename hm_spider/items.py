# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_djangoitem import DjangoItem
from product.models import Product, Category, Tag


class HmSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class HMProductItem(DjangoItem):
    django_model = Product
    tags = scrapy.Field()


class HMTagItem(DjangoItem):
    django_model = Tag


class HMCategoryItem(DjangoItem):
    django_model = Category
