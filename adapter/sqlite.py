#!/usr/bin/env python
# -*- coding: utf-8 -*-


import math
import sqlite3

import config
from .base import BaseAdapter, Cache


class SqliteAdapter(BaseAdapter):

    def __init__(self):
        super(SqliteAdapter, self).__init__()
        self.connect()

    def connect(self):
        self.conn = sqlite3.connect(config.DATABASES['default']['NAME'], isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    @Cache.boot(['page', 'limit'])
    def pager_groups(self, page, limit=config.PAGE_LIMIT):
        page, offset = self.get_offset(page, limit)
        statement = {
            'count': {
                'sql': 'SELECT COUNT(*) AS _count FROM `groups`',
                'parameters': ()
            },
            'data': {
                'sql': 'SELECT * FROM `groups` ORDER BY `group_id` LIMIT ?,?',
                'parameters': (offset, limit)
            }
        }
        return self._pager(statement, page, limit)

    @Cache.boot(['group_id', 'page', 'limit'])
    def pager_hosts(self, group_id, page, limit=config.PAGE_LIMIT):
        page, offset = self.get_offset(page, limit)
        statement = {
            'count': {
                'sql': 'SELECT COUNT(*) AS _count FROM `hosts` WHERE `group_id`=?',
                'parameters': (group_id,)
            },
            'data': {
                'sql': 'SELECT * FROM `hosts` WHERE `group_id`=? ORDER BY `host_id` LIMIT ?,?',
                'parameters': (group_id, offset, limit)
            }
        }
        return self._pager(statement, page, limit)

    @Cache.boot(['group_id', 'host_id', 'page', 'limit'])
    def pager_users(self, group_id, host_id, page, limit=config.PAGE_LIMIT):
        page, offset = self.get_offset(page, limit)
        statement = {
            'count': {
                'sql': 'SELECT COUNT(*) AS _count FROM `users` WHERE `group_id`=? AND `host_id`=?',
                'parameters': (group_id, host_id)
            },
            'data': {
                'sql': 'SELECT * FROM `users` WHERE `group_id`=? AND `host_id`=? ORDER BY `user_id` LIMIT ?,?',
                'parameters': (group_id, host_id, offset, limit)
            }
        }
        return self._pager(statement, page, limit)

    def _pager(self, statement, page, limit):
        self.cursor.execute(statement['count']['sql'], statement['count']['parameters'])
        row = self.cursor.fetchone()
        count = row['_count']
        total = int(math.ceil(float(count) / limit))

        self.cursor.execute(statement['data']['sql'], statement['data']['parameters'])
        data = self.cursor.fetchall()
        result = {
            'current': page,
            'count': count,
            'total': total,
            'items': data
        }
        return result

    @Cache.boot(['text'])
    def search(self, text):
        text = '%s%%' % text.strip()
        result = []
        if text:
            self.cursor.execute('SELECT `host` FROM `hosts` WHERE `host` LIKE ? ORDER BY `host_id` ASC', (text,))
            rows = self.cursor.fetchall()
            for row in rows:
                result.append(row['host'])
        return result
