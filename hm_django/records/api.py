# !/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import hashlib
import logging
from django.http import HttpResponse
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated

from base.views import BaseGenericViewSet
from .models import UpdateRecord
from .services import MessageService

logger = logging.getLogger('hm_django')


def form_valid(request, *args, **kwargs):
    signature = request.GET.get('signature', '')
    timestamp = request.GET.get('timestamp', '')
    nonce = request.GET.get('nonce', '')
    # token = getattr(settings, 'WECHAT', {}).get('token', '')
    token = 'hm_api_token'

    # 计算排序后的哈希值并比较
    sig = hashlib.sha1(''.join(sorted([token, timestamp, nonce])).encode()).hexdigest()
    if sig == signature:
        return HttpResponse(request.GET.get('echostr', ''), content_type='text/plain')
    return HttpResponse('error')


class FormView(BaseGenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UpdateRecord.objects.all()

    def form_save(self, request):
        """存储小程序消息推送id, 参数ids, 逗号分隔"""
        if not request.user.is_authenticated:
            raise NotAuthenticated()
        ids = request.data.get('ids', '')
        if ids:
            try:
                id_list = ids.split(',')
                MessageService.save_form_id(request.user.id, id_list)
                return self.resp_ok('')
            except Exception as e:
                logger.exception(e)
                return self.resp_fail('error')
        return self.resp_fail('error')
