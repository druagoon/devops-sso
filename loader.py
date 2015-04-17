#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sqlite3

import yaml
try:
    import simplejson as json
except ImportError:
    import json

import config
import schema


FILE_PATTERNS = ('.json', '.yaml', '.yml', '.xml')

class Loader(object):

    def __init__(self, **kwargs):
        self.conn = sqlite3.connect(config.DATABASES['default']['NAME'], isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def reload(self):
        self.create_tables()

        group_id, host_id, user_id = 1, 1, 1
        for filename in os.listdir(config.SERVER_DIR):
            name, ext = os.path.splitext(filename)
            if ext in FILE_PATTERNS:
                fullname = os.path.join(config.SERVER_DIR, filename)
                group = getattr(self, 'parse_%s' % ext[1:])(fullname)
                self.clean(group)

                # load host group data
                sql = self.insert_sql('groups', ['group_id', 'name'])
                self.cursor.execute(sql, (group_id, group['sso']['name']))

                # load host data
                hosts = []
                for host in group['sso']['hosts']:
                    # load user data
                    users = []
                    for user in host['users']:
                        users.append((user_id, group_id, host_id, user['user'], user.get('alias') or '', user.get('key') or ''))
                        user_id += 1
                    sql = self.insert_sql('users', ['user_id', 'group_id', 'host_id', 'user', 'alias', 'key'])
                    self.cursor.executemany(sql, users)

                    hosts.append((host_id, group_id, host['host'], host['port'], host['alias'], host['protocol']))
                    host_id += 1
                sql = self.insert_sql('hosts', ['host_id', 'group_id', 'host', 'port', 'alias', 'protocol'])
                self.cursor.executemany(sql, hosts)
                group_id += 1

    def create_tables(self):
        tables = ['groups', 'hosts', 'users']
        for table in tables:
            desc = getattr(schema.Schema, table)()
            self.cursor.executescript(desc)

    @staticmethod
    def clean(group):
        group['sso']['name'] = group['sso']['name'].strip()
        for v in group['sso']['hosts']:
            if ':' in v['host']:
                v['host'], v['port'] = v['host'].split(':', 1)
            if isinstance(v['port'], basestring):
                if not v['port'].isdigit():
                    raise ValueError("Port number must be an integer.")
                v['port'] = int(v['port'])

    @classmethod
    def insert_sql(cls, table, fields):
        sql = 'INSERT INTO `%s` (%s) VALUES (%s)' % (table, cls.safe_fields(fields), cls.placeholders(fields))
        return sql

    @staticmethod
    def safe_fields(fields):
        return ', '.join(map(lambda x: '`%s`' % x.strip('`'), fields))

    @staticmethod
    def placeholders(fields):
        return ', '.join(['?'] * len(fields))

    @staticmethod
    def parse_yaml(filename):
        return yaml.safe_load(open(filename, 'rb'))

    @classmethod
    def parse_yml(cls, *args, **kwargs):
        return cls.parse_yaml(*args, **kwargs)

    @staticmethod
    def parse_json(filename):
        return json.load(open(filename, 'rb'))
