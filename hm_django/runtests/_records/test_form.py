#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from records.services import MessageService
from runtests import BaseTestCase


class FormSaveApiTest(BaseTestCase):
    api = '/api/records/form_save/'

    def test_save_form(self):
        response = self.client.post(self.api, data={})
        self.assert_resp_fail(response, 403)

        user = self.login()
        response = self.client.post(self.api, data={})
        self.assert_resp_fail(response, 400)

        ids = '12322322'
        response = self.client.post(self.api, data={'ids': ids})
        self.assert_resp_ok(response)
        self.assertEqual(MessageService.get_form_id(user.id), ids)
