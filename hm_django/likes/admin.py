from django.contrib import admin
from .models import LikeBrand, LikeProduct


@admin.register(LikeBrand)
class LikeBrandAdmin(admin.ModelAdmin):
    list_display = ['user', 'brand', 'is_valid', 'created_time']
    search_fields = ['brand__name']
    list_filter = ['brand', 'is_valid']


@admin.register(LikeProduct)
class LikeProductAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'is_valid', 'created_time']
    search_fields = ['product__code', 'product__name']
    list_filter = ['is_valid']
