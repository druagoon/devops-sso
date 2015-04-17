#!/usr/bin/env python
# -*- coding: utf-8 -*-


import importlib

from . import base


def get(engine):
    if engine == 'sqlite3':
        engine = 'sqlite'
    name = '%sAdapter' % engine.capitalize()
    mdl = importlib.import_module('adapter.%s' % engine)
    cls = getattr(mdl, name)
    assert issubclass(cls, base.BaseAdapter)
    return cls()
