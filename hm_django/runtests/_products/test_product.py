#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from likes.models import LikeProduct
from product.models import Product
from runtests import BaseTestCase


class ProductApiTestCase(BaseTestCase):
    list_api = '/api/product/'
    category_list = '/api/product/category/'
    like_list = '/api/product/like/'
    like_product = '/api/product/like/{code}/'
    like_category = '/api/product/like_category/'
    product_detail = '/api/product/{code}/'
    test_product_code = '0148033003'

    def test_list(self):
        response = self.client.get(self.list_api)
        self.assert_resp_ok(response)
        self.assertEqual(len(response.data['data']['results']), 0)

        self.create_product()
        response = self.client.get(self.list_api)
        self.assert_resp_ok(response)
        self.assertEqual(len(response.data['data']['results']), 1)

    def test_retrieve(self):
        response = self.client.get(self.product_detail.format(code=self.test_product_code))
        self.assert_resp_fail(response, 404)

        self.create_product(code=self.test_product_code)
        response = self.client.get(self.product_detail.format(code=self.test_product_code))
        self.assert_resp_ok(response)
        self.assertTrue(Product.objects.filter(code=self.test_product_code).exists())

    def test_category(self):
        response = self.client.get(self.category_list)
        self.assert_resp_ok(response)

    def test_like_list(self):
        response = self.client.get(self.like_list)
        self.assert_resp_fail(response, 403)

        self.login()
        response = self.client.get(self.like_list)
        self.assert_resp_ok(response)
        self.assertEqual(len(response.data['data']['results']), 0)

    def test_like_product(self):
        response = self.client.post(self.like_product.format(code=self.test_product_code))
        self.assert_resp_fail(response, 403)  # 没有权限

        user = self.login()
        response = self.client.post(self.like_product.format(code=self.test_product_code))
        self.assert_resp_fail(response, 404)  # 找不到产品

        product = self.create_product(code=self.test_product_code)
        response = self.client.post(self.like_product.format(code=self.test_product_code))
        self.assert_resp_ok(response)  # 正常
        self.assertTrue(LikeProduct.objects.filter(user=user, product=product, is_valid=True).exists())

    def test_like_category(self):
        response = self.client.get(self.like_category)
        self.assert_resp_fail(response, 403)  # 没有权限

        self.login()
        response = self.client.get(self.like_category)
        self.assert_resp_ok(response)
