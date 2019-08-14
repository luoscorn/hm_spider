#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.conf.urls import include, url
from django.conf import settings
from rest_framework_swagger.views import get_swagger_view

urlpatterns = [
    url(r'^product/', include('product.urls')),
    url(r'^brand/', include('product.brand_urls')),
    url(r'^users/', include('users.urls')),
    url(r'^records/', include('records.urls')),
]

if settings.SHOW_DOC:
    schema_view = get_swagger_view(title='HM Spider API')
    urlpatterns += [
        url('^docs/$', schema_view)
    ]
