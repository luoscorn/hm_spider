#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from likes.models import LikeBrand
from runtests import BaseTestCase


class BrandApiTestCase(BaseTestCase):
    list_api = '/api/brand/'
    like_brand_list_api = '/api/brand/like/'
    like_brand_api = '/api/brand/like/{id}/'

    def test_list(self):
        response = self.client.get(self.list_api)
        self.assert_resp_ok(response)
        self.assertEqual(len(response.data['data']['results']), 0)

        self.create_brand()
        response = self.client.get(self.list_api)
        self.assert_resp_ok(response)
        self.assertEqual(len(response.data['data']['results']), 1)

    def test_like_brand_list(self):
        response = self.client.get(self.like_brand_list_api)
        self.assert_resp_fail(response, 403)

        user = self.login()
        response = self.client.get(self.like_brand_list_api)
        self.assert_resp_ok(response)
        self.assertEqual(len(response.data['data']['results']), 0)

        self.like_brand(user, self.create_brand())
        response = self.client.get(self.like_brand_list_api)
        self.assert_resp_ok(response)
        self.assertEqual(len(response.data['data']['results']), 1)

    def test_like_brand(self):
        response = self.client.post(self.like_brand_api.format(id=1))
        self.assert_resp_fail(response, 403)

        user = self.login()
        response = self.client.post(self.like_brand_api.format(id=1))
        self.assert_resp_fail(response, 404)

        brand = self.create_brand()
        response = self.client.post(self.like_brand_api.format(id=brand.id))
        self.assert_resp_ok(response)
        self.assertTrue(LikeBrand.objects.filter(user=user, brand=brand).exists())
