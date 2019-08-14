#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import logging
from django.core.management import BaseCommand
from django_elasticsearch_dsl.registries import registry
from product.models import Product, Brand

logger = logging.getLogger('hm_django')


class Command(BaseCommand):
    help = '商品建立索引'

    def add_arguments(self, parser):
        parser.add_argument('-b', type=str, help='指定品牌(en_name)，可选')
        parser.add_argument('-e', type=str, help='排除品牌(en_name)，可选')

    def handle(self, *args, **options):
        logger.debug(options)
        brand_name = options.get('b')
        e_brand_name = options.get('e')
        if brand_name:
            brand = Brand.objects.filter(en_name__iexact=brand_name).first()
            if not brand:
                logger.error('brand not found')
                return
            self.index_product(brand)
        elif e_brand_name:
            brand = Brand.objects.filter(en_name__iexact=e_brand_name).first()
            if not brand:
                logger.error('brand not found')
                return
            self.index_product(exclude=brand)
        else:
            self.index_product()

    @staticmethod
    def index_product(brand=None, exclude=None):
        qs = Product.objects.filter(is_valid=True)
        if brand:
            qs = qs.filter(brand=brand)
        if exclude:
            qs = qs.exclude(brand=exclude)
        for p in qs:
            logger.debug(f'index: {p.id}')
            registry.update(p)
