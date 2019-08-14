#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_elasticsearch_dsl import Index, DocType, fields
from django_elasticsearch_dsl.registries import registry

from .models import Product

INDEX = Index(settings.PRODUCT_ES_DB_NAME)

INDEX.settings(
    number_of_shards=1,
    number_of_replicas=1
)


@INDEX.doc_type
class ProductDocument(DocType):
    brand = fields.IntegerField(attr='brand.id')
    category = fields.IntegerField(attr='category.id')
    img = fields.NestedField(attr='img_field_indexing', properties={
        'thumbnail': fields.StringField(), 'fullscreen': fields.StringField()
    })
    feature = fields.NestedField(attr='feature_field_indexing', properties={
        'type': fields.StringField(), 'info': fields.ObjectField()
    })
    off = fields.DoubleField(attr='off_field_indexing')
    hot = fields.IntegerField(attr='hot_field_indexing')
    new = fields.DateField(attr='new_field_indexing')

    tags = fields.StringField(attr='tags_indexing', multi=True)

    class Meta(object):
        model = Product
        fields = ('id', 'code', 'gender', 'name', 'desc', 'price', 'white_price')

    def get_queryset(self):
        qs = super(ProductDocument, self).get_queryset()
        return qs.filter(is_valid=True)


@receiver(post_save)
def update_product_doc(sender, **kwargs):
    if 'django_elasticsearch_dsl' not in settings.INSTALLED_APPS:
        return
    from .tasks import sync_product
    app_label = sender._meta.app_label
    instance = kwargs['instance']
    if app_label == 'product':
        if settings.SYNC_ES:
            registry.update(instance)
        if settings.SYNC_PRODUCT:
            sync_product(instance)
    elif app_label == 'productmark':
        if settings.SYNC_ES:
            registry.update(instance)
        if settings.SYNC_PRODUCT:
            sync_product(instance)
    elif app_label == 'browrecord':
        """考虑使用缓存， 这个频率太高了, 暂不更新"""
        # if settings.SYNC_ES:
        #     registry.update(instance)
    elif app_label == 'likeproduct':
        if settings.SYNC_ES:
            registry.update(instance)


@receiver(post_delete)
def delete_product_doc(sender, **kwargs):
    if 'django_elasticsearch_dsl' not in settings.INSTALLED_APPS:
        return
    app_label = sender._meta.app_label
    instance = kwargs['instance']
    if app_label == 'product':
        registry.update(instance)
    elif app_label == 'productmark':
        pass
