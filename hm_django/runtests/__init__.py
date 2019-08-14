#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.test import TestCase
from rest_framework.test import APIClient

from product.models import Brand, Product
from users.models import UserProfile
from users.services import LoginService


class BaseTestCase(TestCase):
    client_class = APIClient

    def assert_resp_ok(self, response):
        """断言请求ok"""
        data = response.json()
        self.assertEqual(response.json().get('status'), 'ok', msg=f'{data.get("msg")}: {data.get("results")}')

    def assert_resp_fail(self, response, code=None):
        """断言请求错误"""
        data = response.json()
        self.assertEqual(data.get('status'), 'fail')
        if code:
            self.assertEqual(code, data.get('code'))

    @staticmethod
    def create_brand(name='测试', en_name='test'):
        b, _ = Brand.objects.get_or_create(name=name, en_name=en_name)
        return b

    @staticmethod
    def like_brand(user, brand):
        from likes.services import LikeServer
        return LikeServer.like_brand(user, brand)

    @classmethod
    def create_product(cls, name='测试商品', code='test-code', brand=None):
        if not brand:
            brand = cls.create_brand()
        p, _ = Product.objects.get_or_create(
            name=name, brand=brand, code=code, group_code=code.split('-')[0], source_url='', html='', price=99,
            white_price=199, raw_products={}, img_urls={}, size_select={}, desc='test'
        )
        return p

    @classmethod
    def create_user(cls):
        user_profile = getattr(cls, '_user_profile', None)
        if user_profile:
            user_profile = UserProfile.objects.filter(id=user_profile.id).first()
        if not user_profile:
            user_profile = LoginService.create_user('test_user')
            setattr(cls, '_user_profile', user_profile)
        return user_profile.user

    def require_login(self, user):
        self.client.force_authenticate(user)

    def login(self):
        user = self.create_user()
        self.require_login(user)
        return user
