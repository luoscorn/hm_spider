#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_FILTER_RANGE, LOOKUP_QUERY_IN, LOOKUP_QUERY_GT, LOOKUP_QUERY_GTE, LOOKUP_QUERY_LT, LOOKUP_QUERY_LTE,
    LOOKUP_FILTER_TERMS, LOOKUP_FILTER_PREFIX, LOOKUP_FILTER_WILDCARD, LOOKUP_QUERY_EXCLUDE)
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend, IdsFilterBackend, OrderingFilterBackend, DefaultOrderingFilterBackend,
    CompoundSearchFilterBackend)
from django_elasticsearch_dsl_drf.viewsets import BaseDocumentViewSet

from base.views import MixinView
from product.services import ProductService
from users.models import UserProfile
from utils.pagination import PlugPageNumberPagination
from .documents import ProductDocument
from .serializers import ProductIndexSerializer


class ProductDocumentView(MixinView, BaseDocumentViewSet):
    document = ProductDocument
    serializer_class = ProductIndexSerializer
    pagination_class = PlugPageNumberPagination
    lookup_field = 'code'
    filter_backends = [
        CompoundSearchFilterBackend, FilteringFilterBackend, IdsFilterBackend, OrderingFilterBackend,
        DefaultOrderingFilterBackend]
    search_fields = ('name', 'desc')

    filter_fields = {
        'id': 'id',
        'name': 'name',
        'gender': 'gender',
        'category': 'category',
        'price': {
            'field': 'price',
            'lookups': [LOOKUP_FILTER_RANGE, LOOKUP_QUERY_GT, LOOKUP_QUERY_GTE, LOOKUP_QUERY_LT, LOOKUP_QUERY_LTE],
        },
        'tags': {
            'field': 'tags',
            # Note, that we limit the lookups of `tags` field in
            # this example, to `terms, `prefix`, `wildcard`, `in` and
            # `exclude` filters.
            'lookups': [LOOKUP_FILTER_TERMS, LOOKUP_FILTER_PREFIX, LOOKUP_FILTER_WILDCARD, LOOKUP_QUERY_IN,
                        LOOKUP_QUERY_EXCLUDE],
        },
        'brand': {
            'field': 'brand',
            'lookups': [LOOKUP_QUERY_IN],
        }
    }
    multi_match_search_fields = {'name': {'boost': 4}, 'desc': None}

    # Define ordering fields
    ordering_fields = {'price': 'price', 'off': 'off', 'hot': 'hot', 'new': 'new'}
    # Specify default ordering
    ordering = ('-hot',)

    def list(self, request, *args, **kwargs):
        """
        搜索商品
        __________________华丽分割线_____________________
        筛选(不加就不传):
        价格区间: price__range=80__99|price__lt=2000(小于2000的)
        品牌: brand=1|brand__in=1__2|brand=like(关注品牌)
        类别: category=1

        排序(ordering):
        价格升序: price
        价格降序: -price
        折扣最大: -off
        上线时间: -new
        最受欢迎(热度): -hot
        """
        request.query_params._mutable = True
        if request.user.is_authenticated:
            try:
                request.query_params['gender'] = request.user.userprofile.gender
            except UserProfile.DoesNotExist:
                request.query_params['gender'] = 'female'
        if request.query_params.get('brand') == 'like':
            del request.query_params['brand']
            if request.user.is_authenticated:
                brand_ids = ProductService.get_like_brand_ids(request.user)
                if brand_ids:
                    request.query_params['brand__in'] = '__'.join([str(i) for i in brand_ids])
        return super(ProductDocumentView, self).list(request, *args, **kwargs)
