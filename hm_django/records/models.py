#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.db import models
import jsonfield
from jsonfield import JSONField


class SpiderRecord(models.Model):
    url = models.URLField()
    html = models.TextField()
    parse_status = models.CharField('解析状态', max_length=64, default='unknow')
    is_valid = models.BooleanField(default=True)
    update_time = models.DateTimeField(default=timezone.now)
    error = models.CharField('错误类型', null=True, blank=True, max_length=128)
    info = models.TextField('信息', null=True, blank=True)

    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '爬虫记录'
        verbose_name_plural = verbose_name


class UpdateRecord(models.Model):
    url = models.URLField()
    code = models.CharField('代码', null=True, blank=True, max_length=128)
    html = models.TextField()
    update_data = jsonfield.JSONField('记录新旧数据')

    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '更新记录'
        verbose_name_plural = verbose_name


class BrowseRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.IntegerField(null=True, blank=True)
    obj = GenericForeignKey("content_type", "object_id")

    info = JSONField(verbose_name='用户数据', null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '浏览记录'
        verbose_name_plural = verbose_name


class MessageRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    data = jsonfield.JSONField('发送的数据包')
    response = jsonfield.JSONField('返回的数据包')
    type = models.CharField('消息类型', max_length=64, default='xcx')
    template_id = models.CharField('模板id', max_length=64)
    status = models.CharField('状态', default='ok', max_length=64)

    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '消息通知记录'
        verbose_name_plural = verbose_name
