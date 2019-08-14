#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import time

import logging
import requests
from django.conf import settings
from django_redis import get_redis_connection

from product.models import Product, Brand, Tag, Category, ProductMark
from utils.celery_app import product_spider_app, sync_app, update_app

logger = logging.getLogger('hm_django')

scrapy_index_url = 'http://localhost:6800'


def check_jobs(spider_name):
    # 检查是否已经运行
    response = requests.get(f'{scrapy_index_url}/listjobs.json', params={'project': 'hm_spider'})
    data = response.json()
    if data.get('status', '') == 'error':
        logger.error(data.get('message', ''))
        return False
    for runner in data.get('running', []):
        if runner.get('spider') == spider_name:
            return True
    return False


def start_update(spider_name):
    # 启动更新spider
    response = requests.post(f'{scrapy_index_url}/schedule.json', data={'project': 'hm_spider', 'spider': spider_name})
    data = response.json()
    if data.get('status') == 'ok':
        logger.info(f'start update product ok:{data.get("jobid", "")}')
        return True
    logger.error(data.get('message', ''))
    return False


def check_spider_url(url) -> bool:
    """检查指定时间内是否爬取过该url"""
    key = 'update_urls'
    con = get_redis_connection()
    t = int(time.time())
    con.zremrangebyscore(key, 0, t - settings.CHECK_PRODUCT_TIME)
    if con.zrank(key, url) is None:
        con.zadd(key, {url: t})
        return False
    return True


@product_spider_app.task
def update_product(spider_name='default_spider_name', urls: list = None):
    """本地的检查更新"""
    logger.info(spider_name)

    con = get_redis_connection()
    if spider_name == 'default_spider_name':
        return
    if not check_jobs(spider_name):
        start_update(spider_name)
    elif urls:
        con.delete(f'{spider_name}:dupefilter')
        for url in urls:
            # 这里检查的是本地有没有更新过
            if check_spider_url(url):
                continue
            con.lpush(f'{spider_name}:start_urls', url)


# -----------------------------------------------------------------
# 服务端使用,服务器端只有beat，只调用，不执行
@update_app.task
def check_product(brand_name, url):
    """远程的调用,发送给爬虫集群,先检查，然后通知内网更新url数据"""
    logger.info(f'check_product:{brand_name}')
    spider_name = f'{brand_name}_update'.lower()

    # 这里检查的是服务器上有没有更新过
    if check_spider_url(url):
        return
    update_product(spider_name, [url])


@sync_app.task
def sync_data(sync_type: str, data, product: Product, mark_type):
    """服务端接收数据，并更新"""
    if sync_type == 'product':
        brand_data = data.pop('brand')
        data['brand'], _ = Brand.objects.get_or_create(en_name=brand_data['en_name'], name=brand_data['name'])
        ps = Product.objects.filter(code=data['code'])
        tags = data.pop('tags')
        category_name = data.pop('category_name')
        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name, href='')
            data['category'] = category
        if ps.exists():
            ps.update(**data)
        else:
            p = ProductMark.objects.filter(product=product).first()
            if not p:
                p = Product.objects.create(**data, product=product, price=product.price, mark_type=mark_type)
            else:
                p.mark_type = mark_type
                p.price = product.price
            for tag in tags:
                t, _ = Tag.objects.get_or_create(name=tag, href='')
                p.tags.add(t)


# 向服务端发送数据
def sync_product(product: Product):
    """发送商品数据"""
    brand_data = {
        'name': product.brand.name,
        'en_name': product.brand.en_name,
        'icon': product.brand.icon,
    }
    data = {
        'brand': brand_data,
        'name': product.name,
        'gender': product.gender,
        'code': product.code,
        'group_code': product.group_code,
        'source_url': product.source_url,
        'white_price': product.white_price,
        'price': product.price,
        'other_style': product.other_style,
        'img_urls': product.img_urls,
        'size_select': product.size_select,
        'size_valid': product.size_valid,
        'desc': product.desc,
        'detail': product.detail,
        'delivery': product.delivery,

        'category_name': product.category.name if product.category else '',
        'tags': list(product.tags.values_list('name', flat=True)),
    }
    sync_data.delay('product', data)
