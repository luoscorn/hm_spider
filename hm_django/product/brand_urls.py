#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.conf.urls import url

from .api import BrandView

urlpatterns = [
    url(r'^$', BrandView.as_view({'get': 'list'})),
    url(r'^like/(?P<id>\d+)/$', BrandView.as_view({'post': 'like'})),
    url(r'^like/', BrandView.as_view({'get': 'user_like'})),
    url(r'^clean_num/', BrandView.as_view({'post': 'clean_like_num'}))
]
