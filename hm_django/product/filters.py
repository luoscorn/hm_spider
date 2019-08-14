#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django_filters.filterset import FilterSet, CharFilter, ChoiceFilter
from .models import Product, Brand
from django.db import models


class ProductFilter(FilterSet):
    ORDER_CHOICES = (
        ('pl', '价格最低'),
        ('ph', '价格最高'),
        ('discount', '折扣最大'),
        ('new', '最新'),
        ('like', '受欢迎程度')
    )
    q = CharFilter(field_name='name', lookup_expr='icontains', label='搜索')
    o = ChoiceFilter(field_name='order', choices=ORDER_CHOICES, method='filter_o', label='排序')

    class Meta:
        model = Product
        fields = {
            'q': ['exact'],
            'o': ['exact'],
            'price': ['gte', 'lte'],
            'brand': ['exact', 'in'],
            'category': ['exact', 'in']
        }

    @staticmethod
    def filter_o(queryset: Product.objects, *args):
        if args[1] == 'pl':
            queryset = queryset.order_by('price')
        elif args[1] == 'ph':
            queryset = queryset.order_by('-price')
        elif args[1] == 'discount':
            queryset = queryset.prefetch_related('productmark').filter(productmark__mark_type='down').order_by(
                '-productmark__change')
        elif args[1] == 'new':
            queryset = queryset.prefetch_related('productmark').filter(productmark__mark_type='new').order_by(
                '-productmark__order')
            return queryset
        elif args[1] == 'like':
            queryset = queryset.annotate(like_count=models.Count('likeproduct')).order_by(
                '-like_count', '-read_count')
        return queryset


class BrandFilter(FilterSet):
    q = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Brand
        fields = {
            'name': ['icontains']
        }
