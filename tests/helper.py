"""Test helper methods."""

from __future__ import print_function, unicode_literals

import os
import sys
import time
from betamax import Betamax, BaseMatcher
from betamax_matchers.form_urlencoded import URLEncodedBodyMatcher
from functools import wraps
from praw import Reddit
from requests.compat import urljoin


USER_AGENT = 'PRAW_test_suite'


class BodyMatcher(BaseMatcher):
    name = 'PRAWBody'

    def match(self, request, recorded_request):
        if not recorded_request['body']['string'] and not request.body:
            return True
        return URLEncodedBodyMatcher().match(request, recorded_request)


class BasicHelper(object):
    def configure(self):
        self.r = Reddit(USER_AGENT, disable_update_check=True)
        self.sr = 'reddit_api_test'
        self.multi_name = "publicempty"
        self.priv_sr = 'reddit_api_test_priv'
        self.un = 'PyAPITestUser2'
        self.other_user_name = 'PyAPITestUser3'
        self.other_non_mod_name = 'PyAPITestUser4'
        self.invalid_user_name = 'PyAPITestInvalid'
        self.un_pswd = '1111'
        self.other_user_pswd = '1111'
        self.other_non_mod_pswd = '1111'

        if self.r.config.is_reddit:
            self.comment_url = self.url('/r/redditdev/comments/dtg4j/')
            self.link_id = 't3_dtg4j'
            self.link_url = self.url('/r/UCSantaBarbara/comments/m77nc/')
            self.link_url_link = 'http://imgur.com/Vr8ZZ'
            self.more_comments_url = self.url('/r/redditdev/comments/yjk55')
            self.other_user_id = '6c1xj'
            self.priv_submission_id = '16kbb7'
            self.refresh_token = {
                'creddits':        'jLC5Yw9LgoNr4Ldd9j1ESuqJ5DE',
                'edit':            'FFx_0G7Zumyh4AWzIo39bG9KdIM',
                'history':         'j_RKymm8srC3j6cxysYFQZbB4vc',
                'identity':        'E4BgmO7iho0KOB1XlT8WEtyySf8',
                'modconfig':       'bBGRgMY9Ai9_SZLZsaFvS647Mgk',
                'modflair':        'UrMbtk4bOa040XAVz0uQn2gTE3s',
                'modlog':          'ADW_EDS9-bh7Zicc7ARx7w8ZLMA',
                'modposts':        'Ffnae7s4K-uXYZB5ZaYJgh0d8DI',
                'mysubreddits':    'O7tfWhqem6fQZqxhoTiLca1s7VA',
                'privatemessages': 'kr_pHPO3sqTn_m5f_FX9TW4joEU',
                'read':            '_mmtb8YjDym0eC26G-rTxXUMea0',
                'submit':          'k69WTwa2bEQOQY9t61nItd4twhw',
                'subscribe':       'LlqwOLjyu_l6GMZIBqhcLWB0hAE',
                'vote':            '5RPnDwg56vAbf7F9yO81cXZAPSQ'}
            self.submission_edit_id = '16i92b'
        else:
            self.comment_url = self.url(
                '/r/reddit_api_test/comments/iq/_/3a7/')
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

    def first(self, seq, predicate):
        first_hit = next((x for x in seq if predicate(x)), None)
        # Usage of self.assertTrue assumes all inheritance of this Class also
        # inherits from unittest.Testcase
        # pylint: disable-msg=E1101
        self.assertTrue(first_hit is not None)
        return first_hit

    def url(self, path):
        # pylint: disable-msg=W0212
        return urljoin(self.r.config._site_url, path)


class AuthenticatedHelper(BasicHelper):
    def configure(self):
        super(AuthenticatedHelper, self).configure()
        self.r.login(self.un, self.un_pswd)


Betamax.register_request_matcher(BodyMatcher)
with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'
    config.default_cassette_options['match_requests_on'].append('PRAWBody')


def betamax(function):
    @wraps(function)
    def betamax_function(obj):
        with Betamax(obj.r.handler.http).use_cassette(function.__name__):
            # We need to set the delay to zero for betamaxed requests.
            # Unfortunately, we don't know if the request actually happened so
            # tests should only be updated one at a time rather than in bulk to
            # prevent exceeding reddit's rate limit.
            obj.r.config.api_request_delay = 0
            return function(obj)
    return betamax_function


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


def prompt(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()
    response = ''
    cur = ''
    while cur != '\n':
        cur = sys.stdin.read(1)
        response += cur
    return response.strip()


def reddit_only(function):
    @wraps(function)
    def reddit_only_function(obj):
        if obj.r.config.is_reddit:
            return function(obj)
        print('Passing reddit only test: {0}.{1}'
              .format(obj.__class__.__name__, function.__name__))
    return reddit_only_function
