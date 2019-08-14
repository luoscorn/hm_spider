#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import jsonfield
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django_elasticsearch_dsl_drf.wrappers import dict_to_obj


class Category(models.Model):
    name = models.CharField('分类名', max_length=128)
    href = models.CharField('链接', max_length=256, null=True, blank=True)

    order = models.IntegerField('排序', default=0)
    is_valid = models.BooleanField('是否有效', default=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name
        ordering = ('order', '-created_time')

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('标签名', max_length=128)
    href = models.CharField('链接', max_length=256, null=True, blank=True)

    order = models.IntegerField('排序', default=0)
    is_valid = models.BooleanField('是否有效', default=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '商品标签'
        verbose_name_plural = verbose_name
        ordering = ('order', '-created_time')

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField('牌子', db_index=True, max_length=128)
    en_name = models.CharField('英文名', db_index=True, max_length=128)
    icon = models.CharField('图标', max_length=256, null=True, blank=True)
    domain = models.CharField('官网', max_length=256, null=True, blank=True)

    order = models.IntegerField('排序', default=0)
    is_valid = models.BooleanField('是否有效', default=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '品牌'
        verbose_name_plural = verbose_name
        ordering = ('order', '-created_time')

    def __str__(self):
        return self.name


class Product(models.Model):
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
        ('other', '其他')
    )
    brand = models.ForeignKey(Brand, verbose_name='品牌', on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField('商品名', max_length=256)
    gender = models.CharField('性别', choices=GENDER_CHOICES, default='female', max_length=64)

    code = models.CharField('商品号', db_index=True, unique=True, max_length=64)
    group_code = models.CharField('商品分类', db_index=True, max_length=64)

    source_url = models.CharField('源url', max_length=256)
    html = models.TextField()
    white_price = models.FloatField('原价', max_length=64, default=0)
    price = models.FloatField('实际价格', max_length=64, default=0)

    raw_products = jsonfield.JSONField('相关产品原始数据')
    other_style = jsonfield.JSONField('其他款式数据', null=True, blank=True)
    img_urls = jsonfield.JSONField()
    size_select = jsonfield.JSONField()
    size_valid = jsonfield.JSONField(null=True, blank=True)

    desc = models.TextField('描述', blank=True, null=True)
    detail = jsonfield.JSONField('细节', blank=True, null=True)
    delivery = models.TextField('配送信息', blank=True, null=True)

    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, verbose_name='标签', blank=True)
    # start_time = models.DateTimeField('开始售卖时间', null=True, blank=True)
    # end_time = models.DateTimeField('售卖结束时间', null=True, blank=True)

    read_count = models.IntegerField('查看数量', default=0)  # 定时刷新

    order = models.IntegerField('排序', default=0)
    is_valid = models.BooleanField('是否有效', default=True)
    update_time = models.DateTimeField('更新时间', default=now)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = verbose_name
        ordering = ('order', '-created_time')

    def __str__(self):
        return f'{self.name}: {self.code}'

    def show_tags(self):
        return '-'.join([tag.name for tag in self.tags.all()])

    show_tags.short_description = '标签'

    def show_detail(self):
        return self.detail

    show_detail.short_description = '细节'

    def show_valid_size(self):
        if not self.size_valid or not isinstance(self.size_valid, dict):
            return
        valid_sizes: list = self.size_valid.get('availability', [])
        if valid_sizes and isinstance(self.size_select, list):
            valid_ = []
            for size in self.size_select:
                if size.get('sizeCode') in valid_sizes:
                    valid_.append(size.get('name'))
            return f'{"|".join(valid_)}'

    show_valid_size.short_description = '可购尺码'

    @property
    def img_field_indexing(self):
        if self.img_urls and isinstance(self.img_urls, list):
            return dict_to_obj(self.img_urls[0])

    @property
    def feature_field_indexing(self):
        mark: ProductMark = self.productmark_set.first()
        feature = {'type': '', 'info': {}}
        if mark:
            info = {}
            if mark.mark_type == 'down':
                info = {'discount': round(mark.change / self.white_price, 2)}
            feature = {'type': mark.mark_type, 'info': info}
        return dict_to_obj(feature)

    @property
    def off_field_indexing(self):
        return round((self.white_price - self.price) * 100 / self.white_price,
                     2) if self.price < self.white_price else 0.0

    @property
    def hot_field_indexing(self):
        return self.likeproduct_set.count() * 2 + self.get_read_count()

    @property
    def new_field_indexing(self):
        pm = self.productmark_set.filter(mark_type='new').first()
        if pm:
            return pm.update_time if pm.update_time else pm.created_time
        return self.update_time

    def get_read_count(self):
        content_type = ContentType.objects.get_for_model(self)
        from records.models import BrowseRecord
        return BrowseRecord.objects.filter(content_type=content_type, object_id=self.id).count()

    @property
    def tags_indexing(self):
        return [tag.name for tag in self.tags.filter(is_valid=True)]


class ProductMark(models.Model):
    TYPE_CHOICES = (
        ('new', '新品'),
        ('down', '降价'),
        ('recommend', '推荐')
    )
    product = models.ForeignKey(Product, verbose_name='产品', on_delete=models.SET_NULL, null=True, blank=True)
    mark_type = models.CharField('标记类型', choices=TYPE_CHOICES, max_length=64)
    price = models.FloatField('价格', null=True, blank=True)  # 冗余数据
    change = models.FloatField('价格变化', db_index=True, null=True, blank=True)
    order = models.IntegerField('排序', default=0)

    update_time = models.DateTimeField('更新时间', null=True, blank=True)
    is_valid = models.BooleanField('是否有效', default=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '产品标记'
        verbose_name_plural = verbose_name
        ordering = ['order', '-created_time']


@receiver(post_save, sender=ProductMark)
def update_product(**kwargs):
    from records.services import MessageService
    instance: ProductMark = kwargs.get('instance', None)
    if instance:
        if instance.mark_type == 'new':
            for lb in instance.product.brand.likebrand_set.all():
                if MessageService.msg_send(lb.user):
                    MessageService.send_new_msg(lb.user, instance.product.brand)
        if instance.mark_type == 'down':
            for lp in instance.product.likeproduct_set.all():
                if MessageService.msg_send(lb.user):
                    MessageService.send_depreciate_msg(lp.user, lp.product)

