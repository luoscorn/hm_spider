#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.conf import settings
from django.db import models
from jsonfield import JSONField


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女')
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    avatar = models.ImageField('头像', upload_to='users/avatar/%Y/', blank=True, null=True)
    nickname = models.CharField('昵称', max_length=32, null=True, blank=True)
    gender = models.CharField('性别', choices=GENDER_CHOICES, default='male', max_length=16)
    phone = models.CharField('手机', max_length=32, db_index=True, unique=True, null=True, blank=True)
    intro = models.TextField('简介', null=True, blank=True)
    settings = JSONField(verbose_name='配置信息', null=True, blank=True)

    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nickname if self.nickname else ''


class WechatUser(models.Model):
    unionid = models.CharField('微信开放id', max_length=64, null=True, blank=True)
    openid = models.CharField('微信开放id', max_length=64, null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    data = JSONField(verbose_name='用户数据', null=True, blank=True)

    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '微信用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.openid if self.openid else ''
