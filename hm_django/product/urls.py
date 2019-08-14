#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.conf.urls import url

from .api import ProductView, CategoryView
from .search import ProductDocumentView
from django.conf import settings

urlpatterns = [
    url(r'^$', ProductView.as_view({'get': 'list'})),
    url(r'^category/', CategoryView.as_view({'get': 'list'})),
    url(r'^like_category/$', ProductView.as_view({'get': 'like_category'})),
    url(r'^like/$', ProductView.as_view({'get': 'user_like'})),
    url(r'^like/(?P<code>[\d\-\w]+)/$', ProductView.as_view({'post': 'like'})),
    url(r'^(?P<code>[\d\-\w]+)/$', ProductView.as_view({'get': 'retrieve'})),
]

if settings.SYNC_ES:
    urlpatterns.insert(1, url(r'^search/', ProductDocumentView.as_view({'get': 'list'})))
