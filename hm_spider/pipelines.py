#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from django.utils.timezone import now

from hm_spider.items import HMProductItem
from product.models import Product, Tag, Category, Brand, ProductMark
from records.models import UpdateRecord

BRAND_CATEGORY = {
    'hm': 'HM',
    'nike': '耐克',
    'adidas': 'Adidas',
    'zara': 'Zara',
    'lining': '李宁',
    'uniqlo': '优衣库',
    'ur': 'UR',
    'bershka': 'Bershka',
    'gap': 'Gap',
    'forever21': 'Forever21',
    'canda': 'C&A',
    'only': 'Only'
}


class HmSpiderPipeline(object):
    @classmethod
    def get_brand(cls, spider_name: str):
        en_name = spider_name.split('_')[0]
        brand_name = BRAND_CATEGORY.get(spider_name.split('_')[0])
        brand = getattr(cls, '_brand', None)
        if not brand:
            brand, is_created = Brand.objects.get_or_create(en_name=en_name.upper())
            if is_created:
                brand.name = brand_name
                brand.save()
            setattr(cls, '_brand', brand)
        return brand

    def process_item(self, item: HMProductItem, spider: scrapy.Spider):
        if 'update' in spider.name:
            self.update_product(item, spider)
        elif 'new' in spider.name:
            self.new_product(item, spider)
        else:
            self.add_product(item, spider)

    def new_product(self, item: HMProductItem, spider: scrapy.Spider):
        item = self.add_product(item, spider)
        if getattr(item, '_instance'):
            product = item.instance
            self.mark_product(product, 'new')
        return item

    def add_product(self, item: HMProductItem, spider: scrapy.Spider):
        if Product.objects.filter(code=item['code']).exists():
            spider.logger.info(f'exist product: {item["code"]}')
            return item
        item['brand'] = self.get_brand(spider.name)
        if 'category' in item:
            item['category'], _ = Category.objects.get_or_create(**item['category'])
        p = item.save()
        for tag_info in item.get('tags', []):
            tag, _ = Tag.objects.get_or_create(**tag_info)
            p.tags.add(tag)
        return item

    def update_product(self, item: HMProductItem, spider: scrapy.Spider):
        product: Product = Product.objects.filter(code=item['code']).first()
        if product:
            return self.add_product(item, spider)
        update_data = self.diff_product(item, product)
        if not update_data:
            self.update_product_data(update_data, item, product)
            spider.logger.info(f'update product: {product.code}')
        return item

    @classmethod
    def update_product_data(cls, update_data: dict, item: HMProductItem, product: Product):
        product.raw_products = item['raw_products']
        product.html = item['html']
        product.update_time = now()
        product.save()
        if 'price' in update_data:
            cls.mark_product(product, 'down')
        UpdateRecord.objects.create(url=item['source_url'], code=item['code'], update_data=update_data)

    @staticmethod
    def mark_product(product: Product, mark_type):
        pm = ProductMark.objects.filter(product=product).first()
        if not pm:
            pm = ProductMark.objects.create(product=product, price=product.price, mark_type=mark_type)
        else:
            pm.mark_type = mark_type
            pm.price = product.price
        pm.update_time = now()
        pm.change = product.white_price - product.price
        pm.save()

    @staticmethod
    def diff_product(item: HMProductItem, product: Product):
        results = {}
        if item['price'] != product.price:
            results['price'] = [product.price, item['price']]
            product.price = item['price']
        if item['white_price'] != product.white_price:
            results['white_price'] = [product.white_price, item['white_price']]
            product.white_price = item['white_price']
        if item['size_valid'] != product.size_valid:
            results['size_valid'] = [product.size_valid, item['size_valid']]
            product.size_valid = item['size_valid']
        if item['size_select'] != product.size_select:
            results['size_select'] = [product.size_select, item['size_select']]
            product.size_select = item['size_select']
        return results
