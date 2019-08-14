#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.conf import settings
from django.utils.timezone import now
from django.db import models


class LikeProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    note = models.CharField('备注', max_length=255, null=True, blank=True)

    is_valid = models.BooleanField('是否有效', default=True)
    like_time = models.DateTimeField('收藏时间', default=now)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '收藏产品'
        verbose_name_plural = verbose_name


class LikeBrand(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    brand = models.ForeignKey('product.Brand', verbose_name='品牌', on_delete=models.CASCADE)
    note = models.CharField('备注', max_length=255, null=True, blank=True)

    is_valid = models.BooleanField('是否有效', default=True)
    like_time = models.DateTimeField('收藏时间', default=now)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '收藏品牌'
        verbose_name_plural = verbose_name
