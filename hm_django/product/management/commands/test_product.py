#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import logging
from django.core.management import BaseCommand

from product.models import Product, Brand

logger = logging.getLogger('hm_django')


class Command(BaseCommand):
    help = '测试商品数据完整性'

    def add_arguments(self, parser):
        parser.add_argument('-b', type=str, help='指定品牌(en_name)，可选')
        parser.add_argument('-l', type=str, choices=('debug', 'warning', 'error'), default='error', help='检测级别')

    def handle(self, *args, **options):
        logger.debug(options)
        brand = options.get('b')
        leave = options.get('l')
        TestProduct.test_brand()
        TestProduct.test_product(brand, leave)


class TestProduct(object):
    @staticmethod
    def assert_equal(v1, v2):
        assert v1 == v2, f"{v1}不等于 {v2}"

    @staticmethod
    def assert_upper(value: str):
        assert value.upper() == value, f"品牌: {value} 英文名不是大写"

    @staticmethod
    def assert_not_null(value: object):
        assert value is not None

    @classmethod
    def test_brand(cls):
        logger.info('start test brand')
        for brand in Brand.objects.filter(is_valid=True):
            logger.debug(f'test brand: {brand.id}-{brand.name}')
            cls.assert_upper(brand.en_name)

    @staticmethod
    def check_other_style(data: dict):
        codes = []
        for code, v in data.items():
            if not Product.objects.filter(code=code).exists():
                codes.append(code)
            assert 'color' in v and 'color_code' in v
        return codes

    @staticmethod
    def check_img_urls(urls: list):
        for url in urls:
            assert 'thumbnail' in url
            assert 'fullscreen' in url

    @staticmethod
    def check_size_select(sizes: list):
        if sizes:
            for size in sizes:
                assert "sizeCode" in size
                assert "name" in size

    @staticmethod
    def check_size_valid(size_valid: [dict]):
        if size_valid:
            assert 'availability' in size_valid and isinstance(size_valid['availability'], list)

    @classmethod
    def test_product(cls, brand=None, leave='error'):
        logger.info('start test products:')
        ps = Product.objects.filter(is_valid=True)
        if brand:
            ps = ps.filter(brand__en_name__iexact=brand)

        for product in ps:
            logger.debug(f'test product: {product.id}-{product.name}')
            cls.assert_not_null(product.brand)
            assert len(product.code) >= 6, f"code 不得少于6位，请检查,product_id: {product.id}"
            assert product.white_price != 0
            assert product.price != 0
            codes = cls.check_other_style(product.other_style)
            if codes and leave != 'error':
                logger.warning(f'{product.code} 其他款式的商品找不到: {codes}')

            cls.check_img_urls(product.img_urls)
            cls.check_size_select(product.size_select)
            cls.check_size_valid(product.size_valid)
            assert '<p>' not in product.desc
