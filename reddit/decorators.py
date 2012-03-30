# This file is part of reddit_api.
#
# reddit_api is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# reddit_api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with reddit_api.  If not, see <http://www.gnu.org/licenses/>.

import reddit.backport  # pylint: disable-msg=W0611

import six
import sys
import time
import warnings
from functools import wraps
from six.moves import urljoin

from reddit import errors


class Memoize(object):
    """
    Simple memoize decorator with timeout, providing a way to prune out cached
    results based on the first parameter to the memoized function.

    For RedditContentObject methods, this means removal by URL, provided by the
    evict method.
    """

    def __init__(self, func):
        wraps(func)(self)
        self.func = func
        self._cache = {}
        self._timeouts = {}

    def __call__(self, reddit_session, page_url, *args, **kwargs):
        key = (reddit_session, page_url, repr(args),
               frozenset(six.iteritems(kwargs)))
        call_time = time.time()
        self.clear_timeouts(call_time, reddit_session.config.cache_timeout)
        self._timeouts.setdefault(key, call_time)
        if key in self._cache:
            return self._cache[key]
        return self._cache.setdefault(key, self.func(reddit_session, page_url,
                                                     *args, **kwargs))

    def clear_timeouts(self, call_time, cache_timeout):
        """Clears the caches of results which have timed out."""
        for key in list(self._timeouts):
            if call_time - self._timeouts[key] > cache_timeout:
                del self._timeouts[key]
                if key in self._cache:
                    del self._cache[key]

    def evict(self, urls):
        relevant_caches = [k for k in self._cache
                           if k[1].rstrip('.json') in urls]
        for key in relevant_caches:
            del self._cache[key]
            del self._timeouts[key]


class RequireCaptcha(object):
    """Decorator for methods that require captchas."""

    def __init__(self, func):
        wraps(func)(self)
        self.func = func

    def __get__(self, obj, key):
        if obj is None:
            return self
        return self.__class__(self.func.__get__(obj, key))

    def __call__(self, *args, **kwargs):
        captcha_id = None
        while True:
            try:
                if captcha_id:
                    kwargs['captcha'] = self.get_captcha(captcha_id)
                return self.func(*args, **kwargs)
            except errors.BadCaptcha as exception:
                captcha_id = exception.response['captcha']

    def get_captcha(self, captcha_id):
        url = urljoin(self.func.__self__.config['captcha'],
                      captcha_id + '.png')
        sys.stdout.write('Captcha URL: %s\nCaptcha: ' % url)
        sys.stdout.flush()
        captcha = sys.stdin.readline().strip()
        return {'iden': captcha_id, 'captcha': captcha}


class SleepAfter(object):  # pylint: disable-msg=R0903
    """
    A decorator to add to API functions that shouldn't be called too
    rapidly, in order to be nice to the reddit server.

    Every function wrapped with this decorator will use a domain specific
    last_call attribute, so that collectively any one of the funcs won't be
    callable within the site's api_request_delay time; they'll automatically be
    delayed until the proper duration is reached.
    """

    def __init__(self, func):
        wraps(func)(self)
        self.func = func
        self.last_call = {}

    def __call__(self, *args, **kwargs):
        config = args[0].config
        if config.domain in self.last_call:
            last_call = self.last_call[config.domain]
        else:
            last_call = 0
        now = time.time()
        delay = last_call + int(config.api_request_delay) - now
        if delay > 0:
            now += delay
            time.sleep(delay)
        self.last_call[config.domain] = now
        return self.func(*args, **kwargs)


def limit_chars(num_chars=80):
    """
    A decorator to limit the number of chars in a function that outputs a
    string.
    """
    def func_limiter(func):
        @wraps(func)
        def func_wrapper(self, *args, **kwargs):
            value = func(self, *args, **kwargs)
            if len(value) > num_chars:
                value = value[:num_chars - 3] + '...'
            return value
        return func_wrapper
    return func_limiter


def parse_api_json_response(func):  # pylint: disable-msg=R0912
    """Decorator to look at the Reddit API response to an API POST request like
    vote, subscribe, login, etc. Basically, it just looks for certain errors in
    the return string. If it doesn't find one, then it just returns True.
    """
    @wraps(func)
    def error_checked_func(self, *args, **kwargs):
        return_value = func(self, *args, **kwargs)
        allowed = ('captcha', 'data', 'errors', 'kind', 'names', 'next',
                   'prev', 'users')
        if isinstance(return_value, dict):
            for key in return_value:
                if key not in allowed:
                    warnings.warn_explicit('Unknown return key: %s' % key,
                                           UserWarning, '', 0)
            if 'errors' in return_value and return_value['errors']:
                error_list = []
                for error_type, msg, value in return_value['errors']:
                    if error_type in errors.ERROR_MAPPING:
                        if error_type == 'RATELIMIT':
                            _request.evict(args[0])
                        error_class = errors.ERROR_MAPPING[error_type]
                    else:
                        error_class = errors.APIException
                    error_list.append(error_class(error_type, msg, value,
                                                  return_value))
                if len(error_list) == 1:
                    raise error_list[0]
                else:
                    raise errors.ExceptionList(error_list)
        return return_value
    return error_checked_func


def require_login(func):
    """A decorator to ensure that a user has logged in before calling the
    function."""

    @wraps(func)
    def login_reqd_func(self, *args, **kwargs):
        if isinstance(self, RedditContentObject):
            user = self.reddit_session.user
            modhash = self.reddit_session.modhash
        else:
            user = self.user
            modhash = self.modhash

        if user is None or modhash is None:
            raise errors.LoginRequired('`%s` requires login.' % func.__name__)
        else:
            return func(self, *args, **kwargs)
    return login_reqd_func


# Avoid circular import: http://effbot.org/zone/import-confusion.htm
from reddit.objects import RedditContentObject
from reddit.helpers import _request
