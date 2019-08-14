#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import weixin


class XCXWeixinMP(weixin.WeixinMP):
    def template_send(self, template_id, touser, data, url=None, miniprogram=None, **kwargs):
        kwargs.setdefault("template_id", template_id)
        kwargs.setdefault("touser", touser)
        kwargs.setdefault("data", data)
        url and kwargs.setdefault("url", url)
        miniprogram and kwargs.setdefault("miniprogram", miniprogram)
        # print kwargs
        return self.post("/message/wxopen/template/send", kwargs)
