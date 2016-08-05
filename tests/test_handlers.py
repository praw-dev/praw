"""Tests for UnauthenticatedReddit class."""

from __future__ import print_function, unicode_literals

from functools import wraps
from mock import patch
from praw import handlers
from random import choice
from six.moves import cStringIO
from .helper import PRAWTest, betamax


def replace_handler(new_handler):
    def factory(func):
        @wraps(func)
        def wrapped(obj):
            old_handler = obj.r.handler
            obj.r.handler = new_handler
            try:
                retval = func(obj)
            finally:
                obj.r.handler = old_handler
            return retval
        return wrapped
    return factory


class HandlerTest(PRAWTest):
    def setUp(self):
        super(HandlerTest, self).setUp()
        self.cache_store = cStringIO()

    def _cache_hit_callback(self, key):
        pass

    @replace_handler(handlers.RateLimitHandler())
    def test_ratelimit_handlers(self):
        to_evict = self.r.config[choice(list(self.r.config.API_PATHS.keys()))]
        self.assertIs(0, self.r.handler.evict(to_evict))

    @betamax()
    def test_cache_hit_callback(self):
        with patch.object(HandlerTest, '_cache_hit_callback') as mock:
            self.r.handler.cache_hit_callback = self._cache_hit_callback

            # ensure there won't be a difference in the cache key
            self.r.login(self.un, self.un_pswd, disable_warning=True)

            before_cache = list(self.r.get_new(limit=5))
            after_cache = list(self.r.get_new(limit=5))

            self.assertTrue(mock.called)
            self.assertEqual(before_cache, after_cache)
        self.r.handler.cache_hit_callback = None
