#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.conf.urls import url
from users.api import LoginView, UserView

urlpatterns = [
    url(r'^auth/$', LoginView.as_view()),
    url(r'^info/$', UserView.as_view({'get': 'info'})),
    url('^change_gender/$', UserView.as_view({'post': 'change_gender'})),
    url(r'^(?P<user_id>\d+)', UserView.as_view({'get': 'retrieve'})),
]
