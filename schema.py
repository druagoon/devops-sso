#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Schema(object):

    @staticmethod
    def groups():
        desc = '''
            DROP TABLE IF EXISTS `groups`;
            CREATE TABLE `groups` (
                `group_id` INT NOT NULL,
                `name` TEXT NOT NULL,
                PRIMARY KEY (`group_id`)
            );
        '''
        return desc

    @staticmethod
    def hosts():
        desc = '''
            DROP TABLE IF EXISTS `hosts`;
            CREATE TABLE `hosts` (
                `host_id` INT NOT NULL,
                `group_id` INT NOT NULL,
                `host` TEXT NOT NULL,
                `port` INT NOT NULL,
                `alias` TEXT,
                `protocol` TEXT NOT NULL
            );
            CREATE INDEX `host_id` ON `hosts` (`host_id`);
        '''
        return desc

    @staticmethod
    def users():
        desc = '''
            DROP TABLE IF EXISTS `users`;
            CREATE TABLE `users` (
                `user_id` INT NOT NULL,
                `group_id` INT NOT NULL,
                `host_id` INT NOT NULL,
                `user` TEXT NOT NULL,
                `alias` TEXT,
                `key` TEXT
            );
            CREATE INDEX `user_id` ON `users` (`user_id`);
        '''
        return desc
