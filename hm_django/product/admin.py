#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.contrib import admin
from .models import Product, Tag, Category, Brand, ProductMark


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['code', 'brand', 'name', 'category', 'white_price', 'price', 'source_url']
    list_filter = ['gender', 'brand']
    search_fields = ['name', 'code']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'href']
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'href']
    search_fields = ['name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']


@admin.register(ProductMark)
class ProductMarkAdmin(admin.ModelAdmin):
    list_display = ['product', 'mark_type', 'price', 'change', 'order']
    search_fields = ['product_id', 'product_code']
    list_filter = ['mark_type']
    raw_id_fields = ['product']
