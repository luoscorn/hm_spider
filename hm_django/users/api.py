#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_jwt.views import ObtainJSONWebToken

from base.views import BaseModelViewSet
from .models import UserProfile
from .serializers import LoginSerializer, UserSerializer


class LoginView(ObtainJSONWebToken):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def get_serializer(self, *args, **kwargs):
        if not hasattr(self, '_serializer'):
            setattr(self, '_serializer', super(LoginView, self).get_serializer(*args, **kwargs))
        return getattr(self, '_serializer')

    def post(self, request, *args, **kwargs):
        """登录(login_type:wechat)"""
        response = super(LoginView, self).post(request, *args, **kwargs)
        serializer = self.get_serializer()
        user = serializer.object.get('user')
        data = response.data.copy()
        if user:
            data['user_info'] = UserSerializer(user.userprofile).data
        return BaseModelViewSet.resp_ok(data)


class UserView(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.filter(user__is_active=True)
    serializer_class = UserSerializer
    lookup_field = 'user_id'

    def get_object(self):
        if self.action == 'info':
            return self.request.user.userprofile
        return super(UserView, self).get_object()

    def retrieve(self, request, *args, **kwargs):
        """获取其他用户信息"""
        return super(UserView, self).retrieve(request, *args, **kwargs)

    def change_gender(self, request):
        """修改性别(不需要参数)"""
        try:
            user_profile = request.user.userprofile
            user_profile.gender = 'female' if user_profile.gender == 'male' else 'male'
            user_profile.save()
        except UserProfile.DoesNotExist:
            return self.resp_fail('用户信息不完整')
        return self.resp_ok(user_profile.gender)

    def info(self, request, *args, **kwargs):
        """获取当前用户信息"""
        return self.retrieve(request, *args, **kwargs)
