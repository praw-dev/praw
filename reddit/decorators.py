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

    def __init__(self, function):
        wraps(function)(self)
        self.function = function
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
        return self._cache.setdefault(key, self.function(reddit_session,
                                                         page_url, *args,
                                                         **kwargs))

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

    def __init__(self, function):
        wraps(function)(self)
        self.function = function

    def __get__(self, obj, key):
        if obj is None:
            return self
        return self.__class__(self.function.__get__(obj, key))

    def __call__(self, *args, **kwargs):
        captcha_id = None
        while True:
            try:
                if captcha_id:
                    # Differentiate between bound and unbound methods
                    if hasattr(self.function, '__self__'):
                        reddit_session = self.function.__self__
                    else:
                        reddit_session = args[0]
                    kwargs['captcha'] = self.get_captcha(reddit_session,
                                                         captcha_id)
                return self.function(*args, **kwargs)
            except errors.BadCaptcha as exception:
                captcha_id = exception.response['captcha']

    def get_captcha(self, reddit_session, captcha_id):
        url = urljoin(reddit_session.config['captcha'],
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

    def __init__(self, function):
        wraps(function)(self)
        self.function = function
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
        return self.function(*args, **kwargs)


def limit_chars(num_chars=80):
    """
    A decorator to limit the number of chars in a function that outputs a
    string.
    """
    def function_limiter(function):
        @wraps(function)
        def function_wrapper(self, *args, **kwargs):
            value = function(self, *args, **kwargs)
            if len(value) > num_chars:
                value = value[:num_chars - 3] + '...'
            return value
        return function_wrapper
    return function_limiter


def parse_api_json_response(function):  # pylint: disable-msg=R0912
    """Decorator to look at the Reddit API response to an API POST request like
    vote, subscribe, login, etc. Basically, it just looks for certain errors in
    the return string. If it doesn't find one, then it just returns True.
    """
    @wraps(function)
    def error_checked_function(self, *args, **kwargs):
        return_value = function(self, *args, **kwargs)
        allowed = ('captcha', 'data', 'errors', 'kind', 'names', 'next',
                   'prev', 'ratelimit', 'users')
        if isinstance(return_value, dict):
            for key in return_value:
                if key not in allowed:
                    warnings.warn_explicit('Unknown return key: %s' % key,
                                           UserWarning, '', 0)
            if 'errors' in return_value and return_value['errors']:
                # Hack for now with successful submission and captcha error
                if 'data' in return_value and 'url' in return_value['data']:
                    return return_value
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
    return error_checked_function


def require_login(function):
    """Ensure that the user has logged in before calling the function."""

    @wraps(function)
    def login_required_function(self, *args, **kwargs):
        if isinstance(self, RedditContentObject):
            user = self.reddit_session.user
            modhash = self.reddit_session.modhash
        else:
            user = self.user
            modhash = self.modhash

        if user is None or modhash is None:
            raise errors.LoginRequired('%r requires login' % function.__name__)
        else:
            return function(self, *args, **kwargs)
    return login_required_function


def require_moderator(function):
    """Ensure that the user is a moderator of the subreddit."""

    @wraps(function)
    def moderator_required_function(self, subreddit, *args, **kwargs):
        if not self.user.is_mod:
            raise errors.ModeratorRequired('%r is not moderator' %
                                           six.text_type(self.user))
        if self.user._mod_subs is None:
            self.user._mod_subs = {'mod': self.get_subreddit('mod')}
            for sub in self.user.my_moderation(limit=None):
                self.user._mod_subs[six.text_type(sub).lower()] = sub
        if six.text_type(subreddit).lower() not in self.user._mod_subs:
            raise errors.ModeratorRequired('%r is not a moderator of %r' %
                                           (six.text_type(self.user),
                                            six.text_type(subreddit)))
        return function(self, subreddit, *args, **kwargs)
    return moderator_required_function


# Avoid circular import: http://effbot.org/zone/import-confusion.htm
from reddit.objects import RedditContentObject
from reddit.helpers import _request
