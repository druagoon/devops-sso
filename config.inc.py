# !/usr/bin/env python
#  -*- coding: utf-8 -*-


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import locale
import logging
import logging.config

locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
code = locale.getpreferredencoding()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
DATA_DIR = os.path.join(BASE_DIR, 'data')
SERVER_DIR = os.path.join(DATA_DIR, 'servers')
DB_DIR = os.path.join(DATA_DIR, 'db')

for p in [LOG_DIR, DATA_DIR, SERVER_DIR, DB_DIR]:
    if not os.path.isdir(p):
        os.makedirs(p, 0755)

# 分页数
PAGE_LIMIT = 20

# 窗口布局比例
WINDOW_SCALE = '7:3'

# ssh连接超时时间 (单位: 秒)
SSH_CONNECT_TIMEOUT = 15

ENGINE = 'sqlite3'

DATABASES = {
    'default': {
        'NAME': os.path.join(DB_DIR, 'sso.db'),
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'detail': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d [%(pathname)s:%(lineno)d] %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'NOTSET',
            'class': 'logging.StreamHandler',
            'stream': sys.stderr,
            'formatter': 'detail'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'sso.log'),
            'formatter': 'detail',
            'maxBytes': 32 * 1024 * 1024,
            'backupCount': 10,
        },
    },
    'loggers': {
        'common': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

logging.config.dictConfig(LOGGING)
