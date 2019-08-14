#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import datetime
import logging
from django.conf import settings
from django.core.cache import cache
from weixin import WeixinError

from product.models import Brand
from .models import MessageRecord, BrowseRecord

logger = logging.getLogger('hm_django')


class MessageService(object):
    @staticmethod
    def save_form_id(user_id, id_list: list):
        """保存form id"""
        cache_key = f'user_xcx_form_id_{user_id}'
        results = cache.get(cache_key, [])
        for form_id in id_list:
            if ' ' in form_id:
                logger.info(f'error form id: {form_id}')
                continue
            results.append({
                'form_id': form_id,
                'datetime': datetime.datetime.now()
            })
        # save to redis
        cache.set(cache_key, results, 7 * 24 * 60 * 60)

    @staticmethod
    def get_form_id(user_id):
        """获取form id"""
        cache_key = f'user_xcx_form_id_{user_id}'
        results = cache.get(cache_key, [])
        fail_ids = []
        now = datetime.datetime.now() + datetime.timedelta(minutes=3)
        form_id = None
        for index, form in enumerate(results):
            fail_ids.append(index)
            if form['datetime'] + datetime.timedelta(days=7) > now:
                form_id = form['form_id']
                break
        if fail_ids:
            # 删除失效的
            for index in fail_ids[::-1]:
                del results[index]
        if results:
            cache.set(cache_key, results, cache.ttl(cache_key))
        else:
            cache.delete(cache_key)
        return form_id

    @classmethod
    def send_xcx_message(cls, user, template_id, data, page):
        from base.wechat import XCXWeixinMP
        openid = user.wechatuser.openid
        form_id = cls.get_form_id(user.id)
        if not form_id:
            return False
        kwargs = {'user': user, 'data': data, 'template_id': template_id}
        try:
            kwargs['response'] = dict(XCXWeixinMP(
                settings.WEIXIN_APP_ID,
                settings.WEIXIN_APP_SECRET).template_send(template_id, openid, data, form_id=form_id, page=page))
        except WeixinError:
            kwargs['status'] = 'fail'
        MessageRecord.objects.create(**kwargs)
        return 'status' not in kwargs

    @classmethod
    def send_depreciate_msg(cls, user, product):
        data = {
            'keyword1': {'value': product.name},
            'keyword2': {'value': product.likeproduct_set.first().like_time.strftime(
                '%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')},
            'keyword3': {'value': str(product.white_price)},
            'keyword4': {'value': product.update_time.strftime('%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')},
            'keyword5': {'value': str(product.price)},
            'keyword6': {'value': '价格下降有时效哦~'},
            'keyword7': {'value': '陪你互娱友情提示'}
        }
        return cls.send_xcx_message(user, settings.WEIXIN_MESSAGE_ID_DEPRECIATE, data=data,
                                    page=f'product?code={product.code}')

    @classmethod
    def send_new_msg(cls, user, brand: Brand):
        """ 发送新增商品消息"""
        data = {
            'keyword1': {'value': brand.name},
            'keyword2': {'value': datetime.datetime.now().strftime(
                '%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')},
        }
        return cls.send_xcx_message(user, settings.WEIXIN_MESSAGE_ID_NEW, data=data,
                                    page=f'pages/collection/collection')

    @staticmethod
    def msg_send(user):
        """查询是否可以给用户发送过服务消息"""
        cache_key = "wcx_msg_sended_time_{}".format(user.id)
        result = cache.get(cache_key, None)
        delta = datetime.timedelta(days=settings.MSG_SEND_DELAY)
        if not result:
            cache.set(cache_key, datetime.datetime.now())
            return True
        if datetime.datetime.now() > result + delta:
            return True
        else:
            return False


class RecordService(object):
    @staticmethod
    def record_browse(user, obj):
        if user.is_authenticated:
            BrowseRecord.objects.create(user=user, obj=obj)
