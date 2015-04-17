#!/usr/bin/env python
# -*- coding: utf-8 -*-


import abc
import hashlib
import inspect
import functools


class BaseAdapter(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    def get_offset(self, page, limit):
        if page < 1:
            page = 1
        offset = (page - 1) * limit
        return page, offset

    @abc.abstractmethod
    def pager_groups(self, page, limit):
        pass

    @abc.abstractmethod
    def pager_hosts(self, group_id, page, limit):
        pass

    @abc.abstractmethod
    def pager_users(self, group_id, host_id, page, limit):
        pass

    @abc.abstractmethod
    def search(self, text):
        pass


class Cache(object):

    __cache = {}

    @classmethod
    def set(cls, key, value):
        cls.__cache[key] = value

    @classmethod
    def get(cls, key):
        return cls.__cache.get(key)

    @classmethod
    def has(cls, key):
        return key in cls.__cache

    @classmethod
    def boot(cls, keys=None):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if keys:
                    allargs = inspect.getcallargs(func, *args, **kwargs)
                    ident = (hex(id(func)), map(lambda x: allargs[x], keys))
                else:
                    ident = (hex(id(func)), args, kwargs)
                key = hashlib.md5(repr(ident)).hexdigest()
                if not cls.has(key):
                    cls.set(key, func(*args, **kwargs))
                return cls.get(key)
            return wrapper
        return decorator
