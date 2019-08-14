#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.db.models import Q
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly

from base.views import BaseModelViewSet
from likes.services import LikeServer
from product.tasks import check_product
from records.services import RecordService
from users.models import UserProfile
from .filters import ProductFilter, BrandFilter
from .models import Product, Brand, Category
from .serializers import ListProductSerializer, ProductSerializer, BrandSerializer, CategorySerializer, \
    LikeBrandSerializer
from .services import ProductService


class ProductView(BaseModelViewSet):
    permission_classes = [AllowAny]
    queryset = Product.objects.filter(is_valid=True)
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    lookup_field = 'code'

    def get_queryset(self):
        queryset = super(ProductView, self).get_queryset()
        if self.action == 'user_like':
            queryset = queryset.filter(likeproduct__user=self.request.user, likeproduct__is_valid=True)
        elif self.request.user.is_authenticated:
            try:
                queryset = queryset.filter(Q(gender=self.request.user.userprofile.gender) | Q(gender='other'))
            except UserProfile.DoesNotExist:
                pass
        return queryset

    def get_object(self):
        obj: Product = super(ProductView, self).get_object()
        check_product.delay(obj.brand.en_name, obj.source_url)
        RecordService.record_browse(self.request.user, obj)
        return obj

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return super(ProductView, self).get_serializer_class()
        return ListProductSerializer

    def check_permissions(self, request):
        if self.action in ['like', 'user_like', 'like_category']:
            if not request.user.is_authenticated:
                self.permission_denied(request, message='must login')
        return super(ProductView, self).check_permissions(request)

    def retrieve(self, request, *args, **kwargs):
        """获取商品详情"""
        return super(ProductView, self).retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """产品列表"""
        return super(ProductView, self).list(request, *args, **kwargs)

    def like(self, request, *args, **kwargs):
        """收藏产品"""
        obj = self.get_object()
        is_like = LikeServer.like_product(request.user, obj)
        msg = 'like' if is_like else 'unlike'
        return self.resp_ok(msg)

    def like_category(self, request):
        """获取收藏分类"""
        data = ProductService.get_like_category(request.user)
        return self.resp_ok(data)

    def user_like(self, request, *args, **kwargs):
        """获取关注的产品(brand可过滤)"""
        return super(ProductView, self).list(request, *args, **kwargs)


class BrandView(BaseModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Brand.objects.filter(is_valid=True)
    serializer_class = BrandSerializer
    filterset_class = BrandFilter
    lookup_field = 'id'

    def get_queryset(self):
        queryset = super(BrandView, self).get_queryset()
        if self.action == 'user_like':
            queryset = queryset.filter(likebrand__user=self.request.user, likebrand__is_valid=True)
        return queryset

    def get_serializer_class(self):
        if self.action == 'user_like':
            return LikeBrandSerializer
        return super(BrandView, self).get_serializer_class()

    def check_permissions(self, request):
        if self.action in ['like', 'user_like']:
            if not request.user.is_authenticated:
                self.permission_denied(request, message='must login')
        return super(BrandView, self).check_permissions(request)

    def list(self, request, *args, **kwargs):
        """获取品牌列表"""
        return super(BrandView, self).list(request, *args, **kwargs)

    def like(self, request, *args, **kwargs):
        """关注品牌"""
        obj = self.get_object()
        is_like = LikeServer.like_brand(request.user, obj)
        msg = 'like' if is_like else 'unlike'
        return self.resp_ok(msg)

    def user_like(self, request, *args, **kwargs):
        """获取已关注的品牌"""
        return super(BrandView, self).list(request, *args, **kwargs)

    def clean_like_num(self, request):
        """清除关注品牌数量标识"""
        brand_id = request.data.get('brand_id')
        if brand_id:
            LikeServer.clean_brand_new_num(request.user, brand_id=brand_id)
            return self.resp_ok()
        return self.resp_fail()


class CategoryView(BaseModelViewSet):
    permission_classes = [AllowAny]
    queryset = Category.objects.filter(is_valid=True)
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        """获取分类列表"""
        return super(CategoryView, self).list(request, *args, **kwargs)
