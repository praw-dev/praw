"""Test helper methods."""

from __future__ import print_function, unicode_literals

import os
import re
import sys
import time
import unittest
import warnings
from betamax import Betamax, BaseMatcher
from betamax_matchers.form_urlencoded import URLEncodedBodyMatcher
from betamax_matchers.json_body import JSONBodyMatcher
from betamax_serializers import pretty_json
from functools import wraps
from praw import Reddit
from praw.errors import ExceptionList
from requests.compat import urljoin
from six import text_type
from six.moves import cStringIO


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

        return URLEncodedBodyMatcher().match(to_compare, recorded_request) or \
            JSONBodyMatcher().match(to_compare, recorded_request)


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

        self.client_id = 'stJlUSUbPQe5lQ'
        self.client_secret = 'iU-LsOzyJH7BDVoq-qOWNEq2zuI'
        self.redirect_uri = 'https://127.0.0.1:65010/authorize_callback'

        self.comment_url = self.url('/r/redditdev/comments/dtg4j/')
        self.reply_warnings_url = self.url('/r/reddit_api_test/'
                                           'comments/3tvngf/_/cx9lw9x')
        self.link_id = 't3_dtg4j'
        self.link_url = self.url('/r/UCSantaBarbara/comments/m77nc/')
        self.link_url_link = 'http://imgur.com/Vr8ZZ'
        self.more_comments_url = self.url('/r/redditdev/comments/yjk55')
        self.other_user_id = '6c1xj'
        self.priv_submission_id = '16kbb7'
        self.refresh_token = {
            'creddits':         'jLC5Yw9LgoNr4Ldd9j1ESuqJ5DE',
            'edit':             'FFx_0G7Zumyh4AWzIo39bG9KdIM',
            'history':          'j_RKymm8srC3j6cxysYFQZbB4vc',
            'identity':         'E4BgmO7iho0KOB1XlT8WEtyySf8',
            'modconfig':        'bBGRgMY9Ai9_SZLZsaFvS647Mgk',
            'modcontributors':  '7302867-nk3NcmGLLHnaDmFdX26tTjYQcSg',
            'modflair':         'UrMbtk4bOa040XAVz0uQn2gTE3s',
            'modlog':           'ADW_EDS9-bh7Zicc7ARx7w8ZLMA',
            'modothers':        '7302867-uHta-txRBG7sBUx1I3pSNq5UCic',
            'modposts':         'Ffnae7s4K-uXYZB5ZaYJgh0d8DI',
            'modwiki':          '7302867-i8p-LbgK_BvMrMUC7LQjed8r4lM',
            'modwiki+contr':    '7302867-4SqdVJq06cEhNEXMEZZCVZ0qZEg',
            'mysubreddits':     'O7tfWhqem6fQZqxhoTiLca1s7VA',
            'privatemessages':  'kr_pHPO3sqTn_m5f_FX9TW4joEU',
            'read':             '_mmtb8YjDym0eC26G-rTxXUMea0',
            'read+report':      '7302867-nOgTLv05rK1kO9YInHWOPua9sK4',
            'report':           '7302867-MKjaXZ-w6S8-tC-JPs0NogkIHGQ',
            'submit':           'k69WTwa2bEQOQY9t61nItd4twhw',
            'subscribe':        'LlqwOLjyu_l6GMZIBqhcLWB0hAE',
            'vote':             '5RPnDwg56vAbf7F9yO81cXZAPSQ',
            'wikiread':         '7302867-PMZfquNPUVYHcrbJkTYpFe9UdAY'}

        self.other_refresh_token = {
            'read':             '10640071-wxnYQyK9knNV1PCt9a7CxvJH8TI',
            'modself':          '10640071-v2ZWipt20gPZvfBnvILkBUDq0P4',
            'privatemessages':  '10640071-mrScbAkbXyjgvwsAE8zz7vMHO_8',
            'submit':           '10640071-oWSCa5YMSWGQrRCa4fMSO_C1bZg'}

        self.comment_deleted_id = 'ctkznxq'

        self.submission_deleted_id = '3f8q10'
        self.submission_edit_id = '16i92b'
        self.submission_hide_id = '3lchjv'
        self.submission_limit_chars_id = '4umin7'
        self.submission_lock_id = '47rnwf'
        self.submission_sticky_id = '32eucy'
        self.submission_sticky_id2 = '32exei'

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

    def assertExceptionList(self, excClasses, callableObj, *args, **kwargs):
        """Fail unless a praw.errors.ExceptionList with errors of excClasses
        are thrown by callableObj when invoked with arguments args and keyword
        arguments kwargs. If a different type of exception is thrown, it will
        not be caught, and the test case will be deemed to have suffered an
        error, exactly as for an unexpected exception.
        """
        try:
            callableObj(*args, **kwargs)
        except ExceptionList as e:
            errors = [type(error) for error in e.errors]
            not_in = [cls for cls in excClasses
                      if cls not in errors]
            extra = [cls for cls in errors
                     if cls not in excClasses]
            not_in = [getattr(cls, '__name__', str(cls))
                      for cls in not_in]
            extra = [getattr(cls, '__name__', str(cls))
                     for cls in extra]
            if extra:
                raise self.failureException("{0} were raised".format(
                    ", ".join(extra)))
            elif not_in:
                raise self.failureException("{0} were not raised".format(
                    ", ".join(not_in)))
            return e
        else:
            raise self.failureException("ExceptionList not raised")

    def assertRaisesAndReturn(self, excClass, callableObj, *args, **kwargs):
        """Same as assertRaises, but returns the instantiated excClass."""
        try:
            callableObj(*args, **kwargs)
        except excClass as e:
            return e
        else:
            excName = getattr(excClass, '__name__', str(excClass))
            raise self.failureException("{0} not raised".format(excName))

    def assertWarnings(self, warning, callable, *args, **kwds):
        """Fail unless a warning of class warning is triggered
           by callable when invoked with arguments args and keyword
           arguments kwds. If a different type of warning is
           triggered, it will not be caught, and the test case will
           fail unless the given warning is also coincidentally
           triggered.

           http://stackoverflow.com/a/12935176/5155994
        """
        if not isinstance(warning, tuple):
            warning = (warning,)

        badwarnings = any(Warning not in x.__mro__ for x in warning)

        if badwarnings:
            raise TypeError('warning must be a warning class or '
                            'tuple of warning classes')
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter('always')

            callable(*args, **kwds)

            caught = any(item.category in warning for item in warning_list)

            try:
                self.assertTrue(caught)
            except AssertionError:
                wname = ", ".join(w.__name__ for w in warning)
                fname = callable.__name__
                if len(warning) == 1:
                    raise AssertionError('{0} not triggered '
                                         'by {1}'.format(wname, fname))
                else:
                    raise AssertionError('None of the following '
                                         'warnings were '
                                         'triggered by {0}: '
                                         '{1}'.format(fname, wname))

    def assertWarningsRegexp(self, regexp, warning, callable, *args, **kwds):
        """Fail unless a warning of class warning is triggered
           by callable when invoked with arguments args and keyword
           arguments kwds. If a different type of warning is
           triggered, it will not be caught, and the test case will
           fail unless the given warning is also coincidentally
           triggered. This will also fail if the regexp (a valid
           regex string) is not found within the warning
        """
        expected_regex = re.compile(regexp)

        if not isinstance(warning, tuple):
            warning = (warning,)

        badwarnings = any(Warning not in x.__mro__ for x in warning)

        if badwarnings:
            raise TypeError('warning must be a warning class or '
                            'tuple of warning classes')
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter('always')

            callable(*args, **kwds)

            caught = any(item.category in warning for item in warning_list)

            try:
                self.assertTrue(caught)
            except AssertionError:
                wname = ", ".join(w.__name__ for w in warning)
                fname = callable.__name__
                if len(warning) == 1:
                    raise AssertionError('{0} not triggered '
                                         'by {1}'.format(wname, fname))
                else:
                    raise AssertionError('None of the following '
                                         'warnings were '
                                         'triggered by {0}: '
                                         '{1}'.format(fname, wname))
            try:
                caughtwarnmessages = [item.message.args[0] for item
                                      in warning_list if
                                      item.category in warning]

                matches = any(re.search(expected_regex, w) for w
                              in caughtwarnmessages)
                self.assertTrue(matches)
            except AssertionError:
                raise AssertionError('Pattern "{0}" not found in'
                                     'any caught warnings'.format(regexp))

    def assertNoWarnings(self, callable, *args, **kwds):
        """Fail unless no warnings are triggered by callable with
           arguments args and keyword arguments kwds.
        """
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter('always')

            callable(*args, **kwds)
            if len(warning_list) == 1:
                wname, warningmsg = (warning_list[0].category.__name__,
                                     warning_list[0].message.args[0])
                raise AssertionError("A warning with a category of {0} "
                                     "and a message of {1} were triggered "
                                     "by {2}".format(wname, repr(warningmsg),
                                                     callable.__name__))
            elif warning_list:
                wnames = [(w.category.__name__, w.message.args[0])
                          if w.message.args else (w.category.__name__, "")
                          for w in warning_list]
                wnames = ["{}: {}".format(k, repr(v)) for k, v in warnings]
                raise AssertionError("The following warnings were triggered "
                                     "by {0}:\n{1}".format(
                                         callable.__name__,
                                         "    \n".join(wnames)))


class OAuthPRAWTest(PRAWTest):
    def betamax_init(self):
        self.r.set_oauth_app_info(self.client_id,
                                  self.client_secret,
                                  self.redirect_uri)

    def setUp(self):
        self.configure()
        self.r = Reddit(USER_AGENT, site_name='reddit_oauth_test',
                        disable_update_check=True)


Betamax.register_request_matcher(BodyMatcher)
Betamax.register_serializer(pretty_json.PrettyJSONSerializer)

with Betamax.configure() as config:
    if os.getenv('TRAVIS'):
        config.default_cassette_options['record_mode'] = 'none'
    config.cassette_library_dir = 'tests/cassettes'
    config.default_cassette_options['match_requests_on'].append('PRAWBody')
    config.default_cassette_options['serialize_with'] = 'prettyjson'


def betamax(cassette_name=None, pass_recorder=False, **cassette_options):
    """Utilze betamax to record/replay any network activity of the test.

    The wrapped function's `betmax_init` method will be invoked if it exists.

    """
    def factory(function):
        @wraps(function)
        def betamax_function(obj):
            with Betamax(obj.r.handler.http).use_cassette(
                    cassette_name or function.__name__,
                    **cassette_options) as cass:
                # We need to set the delay to zero for betamaxed requests.
                # Unfortunately, we don't know if the request actually happened
                # so tests should only be updated one at a time rather than in
                # bulk to prevent exceeding reddit's rate limit.
                obj.r.config.api_request_delay = 0
                # PRAW's cache is global, so we need to clear it for each test.
                obj.r.handler.clear_cache()
                if hasattr(obj, 'betamax_init'):
                    obj.betamax_init()
                if pass_recorder:
                    return function(obj, cass)
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


def mock_sys_stream(streamname, defaulttext=None):
    def wrapper(f):
        @wraps(f)
        def wrapped(obj):
            stream = cStringIO()
            setattr(sys, streamname, stream)
            if defaulttext is not None:
                stream.write(defaulttext)
                stream.seek(0)
            retval = f(obj)
            setattr(sys, streamname, getattr(sys, "__{}__".format(streamname)))
            return retval
        return wrapped
    return wrapper


def teardown_on_keyboard_interrupt(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyboardInterrupt:
            kwargs.get('self', args[0]).tearDown()
            raise

    return wrapper
