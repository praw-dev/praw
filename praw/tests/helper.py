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
from six import next as six_next

from praw import Reddit


def first(seq, predicate):
    return six_next((x for x in seq if predicate(x)), None)


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
    def interactive_only_function():
        if os.getenv('INTERACTIVE'):
            return function()
        print('Passing interactive only test: {0}'.format(function.__name__))
    return interactive_only_function


def local_only(function):
    @wraps(function)
    def local_only_function():
        if not R.config.is_reddit:
            return function()
        print('Passing local only test: {0}'.format(function.__name__))
    return local_only_function


def reddit_only(function):
    @wraps(function)
    def reddit_only_function():
        if R.config.is_reddit:
            return function()
        print('Passing reddit only test: {0}'.format(function.__name__))
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


def delay(amount=None):
    if amount:
        time.sleep(amount)
    elif R.config.api_request_delay == 0:
        time.sleep(0.1)


def disable_cache():
    R.config.cache_timeout = 0


def url(path):
    # pylint: disable-msg=W0212
    return urljoin(R.config._site_url, path)


def configure():
    R.login(UN, '1111')


USER_AGENT = 'PRAW_test_suite'
R = Reddit(USER_AGENT, disable_update_check=True)
SR = 'reddit_api_test'
PRIV_SR = 'reddit_api_test_priv'
UN = 'PyAPITestUser2'
OTHER_USER_NAME = 'PyAPITestUser3'
INVALID_USER_NAME = 'PyAPITestInvalid'

if R.config.is_reddit:
    COMMENT_URL = url('r/redditdev/comments/dtg4j/')
    LINK_URL = url('/r/UCSantaBarbara/comments/m77nc/')
    LINK_URL_LINK = 'http://imgur.com/Vr8ZZ'
    MORE_COMMENTS_URL = url('/r/redditdev/comments/dqkfz/')
    OTHER_USER_ID = '6c1xj'
    PRIV_SUBMISSION_ID = '16kbb7'
    REFRESH_TOKEN = {
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
    SUBMISSION_EDIT_ID = '16i92b'
else:
    COMMENT_URL = url('/r/reddit_test6/comments/y/')
    LINK_URL = url('/r/reddit_test6/comments/y/')
    LINK_URL_LINK = 'http://google.com/?q=29.9093488449'
    MORE_COMMENTS_URL = url('/r/reddit_test6/comments/y/')
    OTHER_USER_ID = 'pk'
