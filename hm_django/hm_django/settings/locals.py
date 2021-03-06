#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import raven
from .base import *
from .logs import *

DEBUG = True
SHOW_DOC = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hm_spider',
        'USER': 'root',
        'HOST': '127.0.0.1',
        'PASSWORD': '123456',
        'PORT': '3306',
        'CONN_MAX_AGE': 60,
    },
}

CORS_ORIGIN_WHITELIST = [
    '127.0.0.1',
    '127.0.0.1:8000',
    'hm.playneed.cn',
]

ALLOWED_HOSTS = ['hm.playneed.cn', 'localhost','127.0.0.1']

WEIXIN_APP_ID = 'wx7fa2f950abacbeeb'
WEIXIN_APP_SECRET = 'a782e0e22b99cada1acc900964a49eef'
WEIXIN_MESSAGE_ID_DEPRECIATE = 'khh4uAEVb3bNfWk8zci30TiTbFbPTrdCpzo6JFBJ7NI'

token = 'hm_api_token'
url = 'http://hm.playneed.cn/api/records/form'
encode_key = 'fmfnDphlOQo74JfZJhqVXjwGmNdMAEipgOPWLgfbpED'

RAVEN_CONFIG = {
    'dsn': 'https://ad57bd0b13104537bb732ddc2f26add5:8efa160bee6349019ef0c8844b3dd61d@sentry.playneed.cn/6',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.abspath(os.path.dirname(BASE_DIR))),
}
SERVER_REDIS_URL = BASE_REDIS_URL