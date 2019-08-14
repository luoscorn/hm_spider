#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.contrib import admin
from .models import UserProfile, WechatUser


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'nickname']


@admin.register(WechatUser)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'openid']
