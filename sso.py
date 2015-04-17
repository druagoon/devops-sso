# !/usr/bin/env python
#  -*- coding: utf-8 -*-


import os
import sys
import curses
import atexit
import logging
import argparse
import importlib

import config
import loader
import helps
import adapter

logger = logging.getLogger('common')


class Board(object):

    def __init__(self, scr):
        self.scr = scr
        self.boot()

    def boot(self):
        self.scr.clear()
        self.set_color()
        self.scr.nodelay(1)

    def set_color(self):
        r"""文字和背景色设置
        """
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK),
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
        seq = range(1, 4)
        self.color_pair = dict(zip(seq, seq))

    def display(self, text=None, y=None, x=None, color_pair=None):
        if isinstance(text, list):
            text = ''.join(text)

        if not color_pair:
            color_pair = self.color_pair[2]

        if None not in [y, x]:
            self.scr.addstr(y, x, text, curses.color_pair(color_pair))
        else:
            self.scr.addstr(text, curses.color_pair(color_pair))
        self.scr.refresh()


class MainBoard(Board):
    r"""左侧主窗口
    """

    def __init__(self, scr, args):
        super(MainBoard, self).__init__(scr)
        self.args = args
        self.adapter = adapter.get(config.ENGINE)
        self.layer = {}
        self.layer_step = ('group', 'host', 'user')
        self.layer_keys = ('page', 'index', 'search')
        self.current_layer = 'group'
        self.result = {}
        self.help_text = ' | '.join(map(lambda x: '%s:%s' % x, helps.PAGER_SHORTCUT))
        self.reset_layers()

    def reset_layers(self):
        for flag in self.layer_step:
            self.layer[flag] = {}
            self.reset_layer(flag)

    def reset_layer(self, flag, keys=None):
        if not keys:
            keys = self.layer_keys
        for key in keys:
            getattr(self, 'reset_%s' % key)(flag)

    def reset_page(self, flag):
        self.layer[flag]['page'] = 1

    def reset_index(self, flag):
        self.layer[flag]['index'] = None

    def reset_search(self, flag):
        self.layer[flag]['search'] = []

    def reset_reference(self):
        r"""重置基准参考坐标
        """
        self.x = 8
        self.y = 1

    @staticmethod
    def pager_text(data):
        return '页码: %s/%s 总数: %s' % (data['current'], data['total'], data['count'])

    def draw(self, init=True):
        init and self.reset_reference()

        limit = self.args.limit

        # 主机组列表
        self.result['group'] = self.adapter.pager_groups(self.layer['group']['page'], limit=limit)
        self.display('您可以操作管理的主机组: %s [ %s ]' % (self.pager_text(self.result['group']), self.help_text), self.y, 1)

        for i, v in enumerate(self.result['group']['items']):
            self.y += 1
            self.display('[ %s ]  %s' % (i, v['name']), self.y, self.x)
        self.y += 1
        self.display('[ q ]  退出管理', self.y, self.x)

        self.y += 1
        text = '请选择主机组: '
        if self.layer['group']['search']:
            text += ''.join(self.layer['group']['search'])
        self.display(text, self.y, 1)
        self.current_layer = 'group'

        # 主机组主机列表
        if self.layer['group']['index'] is not None:
            group = self.result['group']['items'][self.layer['group']['index']]
            self.result['host'] = self.adapter.pager_hosts(group['group_id'], self.layer['host']['page'], limit=limit)

            self.y += 1
            self.display('您可以操作管理的主机: ', self.y, 1)
            if self.args.show_selected:
                self.display('*** 当前选择: [%s] %s ***' % (self.layer['group']['index'], group['name']), self.y, self.scr.getyx()[1], self.color_pair[3])
            self.display(' %s' % self.pager_text(self.result['host']), self.y, self.scr.getyx()[1])

            for i, v in enumerate(self.result['host']['items']):
                self.y += 1
                self.display('[ %s ]  %s (%s) [%s] (%s)' % (i, v['host'], v['alias'], v['protocol'].upper(), v['port']), self.y, self.x)
            self.y += 1
            self.display('[ q ]  退出管理', self.y, self.x)

            self.y += 1
            text = '请选择主机: '
            if self.layer['host']['search']:
                text += ''.join(self.layer['host']['search'])
            self.display(text, self.y, 1)
            self.current_layer = 'host'

            # 主机帐号列表
            if self.layer['host']['index'] is not None:
                host = self.result['host']['items'][self.layer['host']['index']]
                self.result['user'] = self.adapter.pager_users(group['group_id'], host['host_id'], self.layer['user']['page'], limit=limit)

                self.y += 1
                self.display('您可以操作管理的帐号: ', self.y, 1)
                if self.args.show_selected:
                    self.display('*** 当前选择: [%s] %s (%s) [%s] (%s) ***' % (self.layer['host']['index'], host['host'], host['alias'], host['protocol'].upper(), host['port']), self.y, self.scr.getyx()[1], self.color_pair[3])
                self.display(' %s' % self.pager_text(self.result['user']), self.y, self.scr.getyx()[1])

                for i, v in enumerate(self.result['user']['items']):
                    v = dict(v)
                    self.y += 1
                    self.display('[ %s ]  %s (%s)' % (i, v['user'], v.get('alias') or v['user']), self.y, self.x)
                self.y += 1
                self.display('[ q ]  退出管理', self.y, self.x)

                self.y += 1
                text = '请选择帐号: '
                if self.layer['user']['search']:
                    text += ''.join(self.layer['user']['search'])
                self.display(text, self.y, 1)
                self.current_layer = 'user'

                # 选择帐号
                if self.layer['user']['index'] is not None:
                    user = self.result['user']['items'][self.layer['user']['index']]
                    cmd = ['ssh']
                    cmd.append('-p %s' % host['port'])
                    cmd.append('-o ConnectTimeout=%s' % self.args.timeout)
                    if user['key']:
                        cmd.append('-i %s' % user['key'])
                    cmd.append('%s@%s' % (user['user'], host['host']))
                    cmd = ' '.join(cmd)
                    atexit.register(lambda : os.system('clear && echo "%(cmd)s ..." && echo && %(cmd)s' % {'cmd': cmd}))
                    sys.exit(0)


class SubBoard(Board):
    r"""右侧子窗口
    """

    def __init__(self, main, scr):
        super(SubBoard, self).__init__(scr)
        self.main = main

    def reset_reference(self):
        self.x = self.scr.getmaxyx()[1] / 2
        self.y = 1

    def draw(self, init=True):
        init and self.reset_reference()
        if self.main.layer['group']['index'] is None and self.main.layer['group']['search']:
            text = ''.join(self.main.layer['group']['search'])
            hosts = self.main.adapter.search(text)
            if hosts:
                for host in hosts:
                    self.display(host, self.y, self.x - len(host) / 2)
                    self.y += 1


class SSO(object):

    corner = '+'

    def __init__(self, stdscr, args):
        self.args = args
        self.main = MainBoard(stdscr, args)
        self.main_y, self.main_x = self.main.scr.getmaxyx()
        self.sub_x = self.main_x * self.scale[1] / sum(self.scale)
        sub = self.main.scr.subwin(self.main_y, self.sub_x, 0, self.main_x - self.sub_x)
        self.sub = SubBoard(self.main, sub)

    @property
    def scale(self):
        return map(lambda x: int(x), self.args.scale.split(':'))

    def render(self):
        self.main.scr.clear()
        self.layout()
        self.sub.draw()
        self.main.draw()

    def layout(self):
        r"""窗口布局 初始化边框以及窗口分割线
        """
        border = ''.join([self.corner, '-' * (self.main_x - len(self.corner) * 2), self.corner])

        # 顶部及底部边框
        self.main.display(border, 0, 0, self.main.color_pair[1])
        self.main.display(border, self.main_y - 2, 0, self.main.color_pair[1])

        # 左边及右边边框
        for x in [0, self.main_x - 1]:
            self.main.scr.vline(1, x, '|', self.main_y - 3)

        # 下面不仅可绘制左右边框 并可自定义边框颜色
        # for y in xrange(1, self.main_y - 2):
        #     self.main.display('|', y, 0, self.main.color_pair[1])
        #     self.main.display('|', y, self.main_x - 1, self.main.color_pair[1])

        # 中间窗口分割线
        edge = self.main_x - self.sub_x
        self.main.scr.vline(1, edge, '|', self.main_y - 3)

        # 下面不仅可绘制分割线 并可自定义分割线颜色
        # for y in xrange(1, self.main_y - 2):
        #     self.main.display('|', y, edge, self.main.color_pair[1])

    def receive(self):
        self.main.scr.nodelay(1)
        while 1:
            c = self.main.scr.getch()
            if c in [ord('\x1b')]:  # Esc键
                break
            elif c in [curses.KEY_BACKSPACE, ord('\b')]:
                if self.main.layer[self.main.current_layer]['search']:
                    self.main.layer[self.main.current_layer]['search'] = self.main.layer[self.main.current_layer]['search'][:-1]
                    self.render()
            elif c in [curses.KEY_ENTER, ord('\n'), ord('\r')]:
                text = ''.join(self.main.layer[self.main.current_layer]['search'])
                if text.isdigit():
                    self.main.layer[self.main.current_layer]['index'] = int(text)
                    self.render()
            elif c == curses.KEY_HOME:
                if self.main.layer[self.main.current_layer]['page'] > 1:
                    self.main.layer[self.main.current_layer]['page'] = 1
                    self.render()
            elif c == curses.KEY_END:
                total = self.main.result[self.main.current_layer]['total']
                if self.main.layer[self.main.current_layer]['page'] < total:
                    self.main.layer[self.main.current_layer]['page'] = total
                    self.render()
            elif c == curses.KEY_PPAGE:
                page = self.main.layer[self.main.current_layer]['page']
                total = self.main.result[self.main.current_layer]['total']
                if 1 < page <= total:
                    self.main.layer[self.main.current_layer]['page'] = min(total, max(page-1, 1))
                    self.render()
            elif c == curses.KEY_NPAGE:
                page = self.main.layer[self.main.current_layer]['page']
                total = self.main.result[self.main.current_layer]['total']
                if page < total:
                    self.main.layer[self.main.current_layer]['page'] = min(total, max(page+1, 1))
                    self.render()
            elif 0 < c < 256:
                c = chr(c)
                if c in 'Qq':
                    # 自下而上逐级退出
                    idx = self.main.layer_step.index(self.main.current_layer)
                    if idx == 0:
                        break
                    else:
                        # 重置当前层下标、分页以及搜索文本
                        self.main.reset_layer(self.main.current_layer)

                        # 重置上一层的下标和搜索文本(保留分页)
                        idx -= 1
                        pre_flag = self.main.layer_step[idx]
                        self.main.reset_layer(pre_flag, ['index', 'search'])
                        self.render()
                else:
                    self.main.layer[self.main.current_layer]['search'].append(c)
                    self.render()
        self.main.scr.nodelay(0)


def main(stdscr, args):
    if args.reload:
        loader.Loader().reload()
    sso = SSO(stdscr, args)
    sso.render()
    sso.receive()


def command():
    parser = argparse.ArgumentParser(description='SSO terminal for ops.')
    parser.add_argument('-l', '--limit', dest='limit', action='store', default=config.PAGE_LIMIT, type=int, required=False, help='number per page (default: %s)' % config.PAGE_LIMIT)
    parser.add_argument('-r', '--reload', dest='reload', action='store_true', required=False, help='reload server data to sqlite (default: false)')
    parser.add_argument('-s', '--show_selected', dest='show_selected', action='store_true', required=False, help='show selected group or host (default: false)')
    parser.add_argument('-S', '--scale', dest='scale', action='store', default=config.WINDOW_SCALE, required=False, help='window scale (default: %s)' % config.WINDOW_SCALE)
    parser.add_argument('-t', '--timeout', dest='timeout', action='store', default=config.SSH_CONNECT_TIMEOUT, required=False, help='ssh connect timeout  in seconds (default: %ss)' % config.SSH_CONNECT_TIMEOUT)
    return parser.parse_args()

if __name__ == '__main__':
    args = command()
    curses.wrapper(main, args)
