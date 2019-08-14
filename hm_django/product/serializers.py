#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import time

from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from django_elasticsearch_dsl_drf.wrappers import obj_to_dict
from rest_framework import serializers

from likes.models import LikeProduct
from likes.services import LikeServer
from product.documents import ProductDocument
from product.services import ProductService
from .models import Product, Brand, Category, ProductMark


class ListProductSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    brand_icon = serializers.CharField(source='brand.icon', read_only=True)
    is_like = serializers.SerializerMethodField()
    off = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    feature = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'code', 'img', 'brand_name', 'brand_icon', 'desc', 'price', 'white_price',
                  'name', 'is_like', 'off', 'tags', 'feature')

    @classmethod
    def get_img(cls, obj):
        if obj.img_urls and isinstance(obj.img_urls, list):
            if obj.brand.en_name == 'zara'.upper():
                cls.change_zara_img(list(obj.img_urls))
            return obj.img_urls[0]

    @staticmethod
    def get_feature(obj: Product):
        mark: ProductMark = obj.productmark_set.first()
        if mark:
            info = {}
            if mark.mark_type == 'down':
                info = {'discount': round(mark.change / obj.white_price, 2)}
            return {'type': mark.mark_type, 'info': info}
        return {'type': '', 'info': {}}

    def get_is_like(self, obj: Product):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likeproduct_set.filter(user=request.user, is_valid=True).exists()
        return False

    @classmethod
    def get_images(cls, obj: Product):
        if obj.img_urls:
            if obj.brand.en_name == 'zara'.upper():
                cls.change_zara_img(list(obj.img_urls))
            return obj.img_urls
        return []

    @staticmethod
    def change_zara_img(img_urls):
        ts = str(time.time()).replace('.', '')[:13]
        for img_url in img_urls:
            img_url['thumbnail'] = f"{img_url['thumbnail'].split('?ts')[0]}?ts={ts}"
            img_url['fullscreen'] = f"{img_url['fullscreen'].split('?ts')[0]}?ts={ts}"

    @staticmethod
    def get_tags(obj: Product):
        return obj.tags.values_list('name', flat=True)

    @staticmethod
    def get_off(obj: Product):
        return round((obj.white_price - obj.price) * 100 / obj.white_price, 2) if obj.price < obj.white_price else 0


class ProductSerializer(ListProductSerializer):
    images = serializers.SerializerMethodField()
    other_style = serializers.SerializerMethodField()
    size_select = serializers.SerializerMethodField()
    size_valid = serializers.SerializerMethodField()
    detail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'code', 'brand_name', 'brand_icon', 'price', 'white_price', 'name', 'is_like', 'images',
                  'size_select', 'size_valid', 'detail', 'desc', 'delivery', 'other_style', 'off')

    @staticmethod
    def get_other_style(obj: Product):
        return obj.other_style

    @staticmethod
    def get_size_select(obj: Product):
        return obj.size_select

    @staticmethod
    def get_size_valid(obj: Product):
        return obj.size_valid

    @staticmethod
    def get_detail(obj: Product):
        return obj.detail


class BrandSerializer(serializers.ModelSerializer):
    is_like = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ('id', 'name', 'icon', 'en_name', 'is_like')

    def get_is_like(self, obj: Brand):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.likebrand_set.filter(user=request.user, is_valid=True).exists()
        return False


class LikeBrandSerializer(BrandSerializer):
    new_count = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ('id', 'name', 'icon', 'en_name', 'is_like', 'new_count')

    def get_is_like(self, obj: Brand):
        return True

    def get_new_count(self, obj: Brand):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return LikeServer.like_brand_new_num(request.user, obj.id)
        return 0


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ProductIndexSerializer(DocumentSerializer):
    brand_name = serializers.SerializerMethodField()
    brand_icon = serializers.SerializerMethodField()

    is_like = serializers.SerializerMethodField()
    img = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        document = ProductDocument
        fields = ('id', 'name', 'code', 'brand_name', 'brand_icon', 'desc', 'price', 'white_price', 'off', 'is_like',
                  'img', 'feature', 'tags')

    @staticmethod
    def get_brand_name(obj):
        return ProductService.get_brand(obj.brand).name

    @staticmethod
    def get_brand_icon(obj):
        return ProductService.get_brand(obj.brand).icon

    def get_is_like(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return LikeProduct.objects.filter(user=request.user, is_valid=True, product_id=obj.id).exists()
        return False

    @classmethod
    def get_img(cls, obj):
        if obj.img:
            img = obj_to_dict(obj.img)
            img = img['_d_'] if '_d_' in img else img
            if ProductService.get_brand(obj.brand).en_name == 'zara'.upper():
                ProductSerializer.change_zara_img([img])
            return img

    @staticmethod
    def get_tags(obj):
        if obj.tags:
            return list(obj.tags)
        else:
            return []
