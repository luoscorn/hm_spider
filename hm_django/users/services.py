#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import requests
from PIL import Image as Img
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from io import BytesIO
from unidecode import unidecode
from weixin import Weixin
from weixin.login import WeixinLoginError

from .models import WechatUser, UserProfile

User = get_user_model()


def get_image_content_file(img_data):
    img = Img.open(BytesIO(img_data))
    thumb_io = BytesIO()
    img.save(thumb_io, img.format)
    return ContentFile(thumb_io.getvalue())


def get_img_data(url):
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        return
    if response.status_code == 200:
        return response.content


class LoginService(object):
    @classmethod
    def weixin(cls):
        if not hasattr(cls, '_wx'):
            wx = Weixin(dict(WEIXIN_APP_ID=settings.WEIXIN_APP_ID,
                             WEIXIN_APP_SECRET=settings.WEIXIN_APP_SECRET))
            setattr(cls, '_wx', wx)

        return getattr(cls, '_wx')

    @classmethod
    def wechat_login(cls, code, user_data=None):
        user_data = user_data if user_data else {}
        wx: Weixin = cls.weixin()
        try:
            session_info = dict(wx.jscode2session(code))
        except WeixinLoginError:
            return False
        unionid = session_info.get('unionid', '')
        filter_data = {'unionid': unionid} if unionid else {'openid': session_info.get('openid')}
        wechat_user = WechatUser.objects.filter(**filter_data).first()
        if not wechat_user:
            # save user info to wechatinfo and create user
            wechat_user = cls.create_wechat_user(session_info, user_data)
        return wechat_user

    @classmethod
    def phone_login(cls, phone, code=None, password=None):
        pass

    @classmethod
    @transaction.atomic
    def create_wechat_user(cls, session_info: dict, user_data: dict):
        gender = user_data.get('gender', 1)
        gender = 'male' if gender == 1 else 'female'
        username = session_info.get('unionid', session_info.get('openid'))
        nickname = "".join((i if ord(i) < 128 else '_') for i in unidecode(user_data.get('nickName')))
        userinfo = cls.create_user(username=username, nickname=nickname, avatar_url=user_data.get('avatarUrl'),
                                   gender=gender)
        wechat_user = WechatUser.objects.create(user=userinfo.user, openid=session_info.get('openid'),
                                                unionid=session_info.get('unionid', ''), data=user_data)
        return wechat_user

    @staticmethod
    @transaction.atomic
    def create_user(username, nickname=None, avatar_url=None, gender='male'):
        user = User.objects.create_user(username=username, password=settings.DEFAULT_PASSWORD)
        user_profile = UserProfile(user=user, nickname=nickname, gender=gender)
        if avatar_url:
            img_data = get_img_data(avatar_url)
            user_profile.avatar.save(f'{username}_avatar.jpeg', content=get_image_content_file(img_data))
        user_profile.save()
        return user_profile
