#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.conf.urls import url
from .api import form_valid, FormView

urlpatterns = [
    url(r'^form/$', form_valid),
    url(r'^form_save/$', FormView.as_view({'post': 'form_save'})),
]
