#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.core.cache import cache
from django.utils.timezone import now
import datetime
from product.models import ProductMark
from .models import LikeBrand, LikeProduct


class LikeServer(object):
    @classmethod
    def like_product(cls, user, obj):
        like, is_create = LikeProduct.objects.get_or_create(user=user, product=obj)
        if not is_create:
            like.is_valid = not like.is_valid
            like.save()
        return like.is_valid

    @classmethod
    def like_brand(cls, user, obj):
        like, is_create = LikeBrand.objects.get_or_create(user=user, brand=obj)
        if not is_create:
            like.is_valid = not like.is_valid
            like.save()
        return like.is_valid

    @classmethod
    def like_brand_new_num(cls, user, brand_id):
        """计算收藏品牌更新数量"""
        cache_key = f'like_brands_u{user.id}_b{brand_id}'
        num, cache_time = cache.get(cache_key, (None, None))
        if num is not None:
            return num
        num = 100
        if cache_time and cache_time + datetime.timedelta(minutes=30) > now():
            num = 0
        elif cache_time:
            num = ProductMark.objects.filter(product__brand_id=brand_id, update_time__gt=cache_time).count()
        cache.set(cache_key, [num, now()], 3 * 24 * 60 * 60)
        return num

    @classmethod
    def clean_brand_new_num(cls, user, brand_id):
        cache_key = f'like_brands_u{user.id}_b{brand_id}'
        data = cache.get(cache_key)
        if data:
            num, cache_time = data
            cache.set(cache_key, [None, cache_time], cache.ttl(cache_key))
