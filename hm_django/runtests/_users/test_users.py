#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from runtests import BaseTestCase
from users.models import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUser(BaseTestCase):
    change_gender_api = '/api/users/change_gender/'

    def test_change_gender(self):
        response = self.client.post(self.change_gender_api)
        self.assert_resp_fail(response, 403)
        user = User.objects.create_user(username='test_user_test', password='test_user_test')
        self.require_login(user)
        response = self.client.post(self.change_gender_api)
        self.assert_resp_fail(response, 400)

        user = self.login()
        gender = user.userprofile.gender
        response = self.client.post(self.change_gender_api)
        self.assert_resp_ok(response)
        self.assertNotEqual(UserProfile.objects.get(user_id=user.id).gender, gender)
