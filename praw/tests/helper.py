#!/usr/bin/env python

# This file is part of PRAW.
#
# PRAW is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PRAW is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# PRAW.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable-msg=C0103, C0302, R0903, R0904, W0201

"""Tests. Split into classes according to what they test."""

from __future__ import print_function, unicode_literals

import os
import sys
import time
from functools import wraps
from requests.compat import urljoin

from praw import Reddit

USER_AGENT = 'PRAW_test_suite'


def flair_diff(root, other):
    """Function for comparing two flairlists supporting optional arguments."""
    keys = ['user', 'flair_text', 'flair_css_class']
    root_items = set(tuple(item[key].lower() if key in item and item[key] else
                           '' for key in keys) for item in root)
    other_items = set(tuple(item[key].lower() if key in item and item[key] else
                            '' for key in keys) for item in other)
    return list(root_items - other_items)


def interactive_only(function):
    @wraps(function)
    def interactive_only_function(obj):
        if os.getenv('INTERACTIVE'):
            return function(obj)
        print('Passing interactive only test: {0}.{1}'
              .format(obj.__class__.__name__, function.__name__))
    return interactive_only_function


def local_only(function):
    @wraps(function)
    def local_only_function(obj):
        if not obj.r.config.is_reddit:
            return function(obj)
        print('Passing local only test: {0}.{1}'
              .format(obj.__class__.__name__, function.__name__))
    return local_only_function


def reddit_only(function):
    @wraps(function)
    def reddit_only_function(obj):
        if obj.r.config.is_reddit:
            return function(obj)
        print('Passing reddit only test: {0}.{1}'
              .format(obj.__class__.__name__, function.__name__))
    return reddit_only_function


def prompt(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()
    response = ''
    cur = ''
    while cur != '\n':
        cur = sys.stdin.read(1)
        response += cur
    return response.strip()


class BasicHelper(object):
    def configure(self):
        self.r = Reddit(USER_AGENT, disable_update_check=True)
        self.sr = 'reddit_api_test'
        self.priv_sr = 'reddit_api_test_priv'
        self.un = 'PyAPITestUser2'
        self.other_user_name = 'PyAPITestUser3'
        self.invalid_user_name = 'PyAPITestInvalid'

        if self.r.config.is_reddit:
            self.comment_url = self.url('r/redditdev/comments/dtg4j/')
            self.link_url = self.url('/r/UCSantaBarbara/comments/m77nc/')
            self.link_url_link = 'http://imgur.com/Vr8ZZ'
            self.more_comments_url = self.url('/r/redditdev/comments/dqkfz/')
            self.other_user_id = '6c1xj'
            self.priv_submission_id = '16kbb7'
            self.refresh_token = {
                'edit':            'mFB93g1nlgt57gd2ch9xy8815ng',
                'identity':        'pwKb6vuFpbqTQjLPTBK_4LW0x3U',
                'modconfig':       'm8em73vTHVaA05_DX-m0RHVBXdU',
                'modflair':        'Zt7sl88AKsljl7VS19gifVHNBaU',
                'modlog':          'Ql-qe7ad56-5UsIP4GN14__t_aY',
                'modposts':        'fdbclNlJorCA_GcD42JLxhNM6mc',
                'mysubreddits':    'HCnSeHp9Rw3fdMd9SkEOdNuys2c',
                'privatemessages': 'pu7vyu-RtB5Z2LkmHJnwKxoStqw',
                'read':            'qa43Mc1v9RjsJCm_tjEUFrN27IU',
                'submit':          'DSJdhcEd9vkwHWqRenDiY042iW0',
                'subscribe':       '8xgyDmQm9FOfOmKnhGcA2bvfywg',
                'vote':            'odS8Wkmgt_kgnUiYfvK6v4u1sAQ'}
            self.submission_edit_id = '16i92b'
        else:
            self.comment_url = self.url('/r/reddit_test6/comments/y/')
            self.link_url = self.url('/r/reddit_test6/comments/y/')
            self.link_url_link = 'http://google.com/?q=29.9093488449'
            self.more_comments_url = self.url('/r/reddit_test6/comments/y/')
            self.other_user_id = 'pk'

    def delay(self, amount=None):
        if amount:
            time.sleep(amount)
        elif self.r.config.api_request_delay == 0:
            time.sleep(0.1)

    def disable_cache(self):
        self.r.config.cache_timeout = 0

    def url(self, path):
        # pylint: disable-msg=W0212
        return urljoin(self.r.config._site_url, path)


class AuthenticatedHelper(BasicHelper):
    def configure(self):
        super(AuthenticatedHelper, self).configure()
        self.r.login(self.un, '1111')
