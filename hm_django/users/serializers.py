#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from weixin.login import WeixinLoginError

from .models import UserProfile
from .services import LoginService

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

LOGIN_TYPE = (
    ('phone', _('phone')),
    ('wechat', _('wechat')),
    ('username', _('username')),
)


class LoginSerializer(JSONWebTokenSerializer):
    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['login_type'] = serializers.ChoiceField(write_only=True, choices=LOGIN_TYPE)
        self.fields['code'] = serializers.CharField(write_only=True, required=False)
        self.fields['user_data'] = serializers.JSONField(write_only=True, required=False)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def validate_empty_values(self, data):
        if data.get('login_type', '') in ('wechat',):
            data[self.username_field] = 'none'
            data['password'] = 'none'
        return super(LoginSerializer, self).validate_empty_values(data)

    def validate(self, attrs):
        login_type = attrs.get('login_type', 'username')
        if login_type == 'wechat':
            try:
                return self.auth_wechat(attrs.get('code', ''), attrs.get('user_data', {}))
            except WeixinLoginError:
                raise serializers.ValidationError('login error')
        elif login_type == 'phone':
            return self.auth_phone(attrs.get('username'))
        return super(LoginSerializer, self).validate(attrs)

    def auth_phone(self, phone, ):
        user = LoginService.phone_login(phone, )
        if user:
            return self.get_token(user)
        raise serializers.ValidationError(_('Unable to log in with provided credentials.'))

    def auth_wechat(self, code, user_data=None):
        user_data = user_data if user_data else {}
        wechat_user = LoginService.wechat_login(code, user_data)
        if wechat_user:
            return self.get_token(wechat_user.user)
        raise serializers.ValidationError(_('Unable to log in with provided credentials.'))

    @staticmethod
    def get_token(user):
        payload = jwt_payload_handler(user)
        return {
            'token': jwt_encode_handler(payload),
            'user': user
        }


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('user_id', 'nickname', 'gender', 'intro', 'avatar_url')

    @staticmethod
    def get_avatar_url(obj: UserProfile):
        return settings.HOST_URL + obj.avatar.url
