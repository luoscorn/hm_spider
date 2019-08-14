#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.contrib import admin
from .models import SpiderRecord, MessageRecord, UpdateRecord


@admin.register(SpiderRecord)
class SpiderRecordAdmin(admin.ModelAdmin):
    list_filter = ['parse_status', 'error']
    list_display = ['url', 'parse_status', 'error', 'created_time']
    search_fields = ['url']


@admin.register(MessageRecord)
class MessageRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'status', 'created_time']
    list_filter = ['type', 'status']


@admin.register(UpdateRecord)
class UpdateRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'url', 'created_time']
