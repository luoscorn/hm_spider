#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hm_django.settings')

product_spider_app = Celery(
    "product_spider",
    broker=f'{settings.BASE_REDIS_URL}/3',
    backend=f'{settings.BASE_REDIS_URL}/2',
    include=["product.tasks"])
product_spider_app.config_from_object("django.conf:settings", namespace="CELERY")

# 同步数据， 不需要beat，只需要worker(服务端，用于接收数据)
sync_app = Celery(
    'sync_app', broker=f'{settings.SERVER_REDIS_URL}/5',
    backend=f'{settings.SERVER_REDIS_URL}/4',
    include=["product.tasks"])
sync_app.config_from_object("django.conf:settings", namespace="CELERY")

# 更新数据，不需要beat，只需要worker(客户端接) 服务端发送任务给客户端，客户端获取到数据再通过sync_app 同步到服务端
update_app = Celery(
    'update_app', broker=f'{settings.SERVER_REDIS_URL}/7',
    backend=f'{settings.SERVER_REDIS_URL}/6',
    include=["product.tasks"])
update_app.config_from_object("django.conf:settings", namespace="CELERY")
