"""Test helper methods."""

from __future__ import print_function, unicode_literals

import os
import time
import unittest
from betamax import Betamax, BaseMatcher
from betamax_matchers.form_urlencoded import URLEncodedBodyMatcher
from functools import wraps
from praw import Reddit
from requests.compat import urljoin
from six import text_type


USER_AGENT = 'PRAW_test_suite'


class BodyMatcher(BaseMatcher):
    name = 'PRAWBody'

    def match(self, request, recorded_request):
        if request.headers.get('SKIP_BETAMAX', 0) > 0:
            request.headers['SKIP_BETAMAX'] -= 1
            return False
        if not recorded_request['body']['string'] and not request.body:
            return True

        # Comparison body should be unicode
        to_compare = request.copy()
        to_compare.body = text_type(to_compare.body)

        return URLEncodedBodyMatcher().match(to_compare, recorded_request)


class PRAWTest(unittest.TestCase):
    def configure(self):
        self.r = Reddit(USER_AGENT, disable_update_check=True)
        self.sr = 'reddit_api_test'
        self.priv_sr = 'reddit_api_test_priv'
        self.un = 'PyAPITestUser2'
        self.other_user_name = 'PyAPITestUser3'
        self.other_non_mod_name = 'PyAPITestUser4'
        self.invalid_user_name = 'PyAPITestInvalid'
        self.un_pswd = '1111'
        self.other_user_pswd = '1111'
        self.other_non_mod_pswd = '1111'

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
            'modothers':       '7302867-uHta-txRBG7sBUx1I3pSNq5UCic',
            'modposts':        'Ffnae7s4K-uXYZB5ZaYJgh0d8DI',
            'mysubreddits':    'O7tfWhqem6fQZqxhoTiLca1s7VA',
            'privatemessages': 'kr_pHPO3sqTn_m5f_FX9TW4joEU',
            'read':            '_mmtb8YjDym0eC26G-rTxXUMea0',
            'wikiread':        '7302867-PMZfquNPUVYHcrbJkTYpFe9UdAY',
            'submit':          'k69WTwa2bEQOQY9t61nItd4twhw',
            'subscribe':       'LlqwOLjyu_l6GMZIBqhcLWB0hAE',
            'vote':            '5RPnDwg56vAbf7F9yO81cXZAPSQ'}

        self.other_refresh_token = {
            'modself':        '10640071-v2ZWipt20gPZvfBnvILkBUDq0P4'}

        self.submission_edit_id = '16i92b'

    def delay_for_listing_update(self, duration=0.1):
        if not os.getenv('TRAVIS') and self.r.config.api_request_delay == 0:
            time.sleep(duration)

    def first(self, sequence, predicate):
        first_hit = next((x for x in sequence if predicate(x)), None)
        self.assertTrue(first_hit)
        return first_hit

    def none(self, sequence, predicate):
        self.assertEqual(
            None, next((x for x in sequence if predicate(x)), None))

    def setUp(self):
        self.configure()

    def url(self, path):
        return urljoin(self.r.config.permalink_url, path)


Betamax.register_request_matcher(BodyMatcher)
with Betamax.configure() as config:
    if os.getenv('TRAVIS'):
        config.default_cassette_options['record_mode'] = 'none'
    config.cassette_library_dir = 'tests/cassettes'
    config.default_cassette_options['match_requests_on'].append('PRAWBody')


def betamax(cassette_name=None, **cassette_options):
    """Utilze betamax to record/replay any network activity of the test.

    The wrapped function's `betmax_init` method will be invoked if it exists.

    """
    def factory(function):
        @wraps(function)
        def betamax_function(obj):
            with Betamax(obj.r.handler.http).use_cassette(
                    cassette_name or function.__name__, **cassette_options):
                # We need to set the delay to zero for betamaxed requests.
                # Unfortunately, we don't know if the request actually happened
                # so tests should only be updated one at a time rather than in
                # bulk to prevent exceeding reddit's rate limit.
                obj.r.config.api_request_delay = 0
                # PRAW's cache is global, so we need to clear it for each test.
                obj.r.handler.clear_cache()
                if hasattr(obj, 'betamax_init'):
                    obj.betamax_init()
                return function(obj)
        return betamax_function
    return factory


def flair_diff(root, other):
    """Function for comparing two flairlists supporting optional arguments."""
    keys = ['user', 'flair_text', 'flair_css_class']
    root_items = set(tuple(item[key].lower() if key in item and item[key] else
                           '' for key in keys) for item in root)
    other_items = set(tuple(item[key].lower() if key in item and item[key] else
                            '' for key in keys) for item in other)
    return list(root_items - other_items)
