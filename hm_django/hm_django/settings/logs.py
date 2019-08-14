#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import os

LOG_FILE_PATH = os.path.join(
    os.path.dirname((os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), 'logs',
    "hm-spider-server.log")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] \ '
                      ' [%(levelname)s]- %(message)s'
        },
    },

    'handlers': {
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE_PATH,
            'maxBytes': 1024 * 1024 * 100,  # 100 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },

    'loggers': {
        'django.admin': {
            'handlers': ['sentry', 'file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django': {
            'handlers': ['sentry', 'file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['sentry', 'file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'hm_django': {
            'handlers': ['sentry', 'file', 'console'],
            'level': 'WARNING',
        },
    }
}
