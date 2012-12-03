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

"""
Decorators.

Mainly do two things. Ensure API guidelines are met and prevent unneccesary
failed API requests by testing that the call can be made first. Also limit the
length of output strings and parse json response for certain errors.
"""

import six
import sys
import time
import warnings
from functools import wraps
from requests.compat import urljoin

from praw import errors


class Memoize(object):
    """Memoize decorator with timeout to clear cache of timed out results."""
    @staticmethod
    def normalize_url(url):
        """Strip trailing .json and trailing slashes."""
        if url.endswith('.json'):
            url = url[:-5]
        if url.endswith('/'):
            url = url[:-1]
        return url

    def __init__(self, function):
        wraps(function)(self)
        self.function = function
        self._cache = {}
        self._timeouts = {}

    def __call__(self, reddit_session, page_url, *args, **kwargs):
        normalized_url = self.normalize_url(page_url)
        key = (reddit_session, normalized_url, repr(args),
               frozenset(six.iteritems(kwargs)))
        call_time = time.time()
        self.clear_timeouts(call_time, reddit_session.config.cache_timeout)
        self._timeouts.setdefault(key, call_time)
        if key in self._cache:
            return self._cache[key]
        result = self.function(reddit_session, page_url, *args, **kwargs)
        if kwargs.get('raw'):
            return result
        return self._cache.setdefault(key, result)

    def clear_timeouts(self, call_time, cache_timeout):
        """Clear the cache of timed out results."""
        for key in list(self._timeouts):
            if call_time - self._timeouts[key] > cache_timeout:
                del self._timeouts[key]
                if key in self._cache:
                    del self._cache[key]

    def evict(self, urls):
        """Remove cached RedditContentObject by URL."""
        urls = [self.normalize_url(url) for url in urls]
        relevant_caches = [key for key in self._cache if key[1] in urls]
        for key in relevant_caches:
            del self._cache[key]
            del self._timeouts[key]


class RequireCaptcha(object):
    """Decorator for methods that require captchas."""
    @staticmethod
    def get_captcha(reddit_session, captcha_id):
        url = urljoin(reddit_session.config['captcha'],
                      captcha_id + '.png')
        sys.stdout.write('Captcha URL: %s\nCaptcha: ' % url)
        sys.stdout.flush()
        captcha = sys.stdin.readline().strip()
        return {'iden': captcha_id, 'captcha': captcha}

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


class SleepAfter(object):  # pylint: disable-msg=R0903
    """
    Ensure frequency of API calls doesn't exceed guidelines.

    We are allowed to make a API request every api_request_delay seconds as
    specified in praw.ini. This value may differ from reddit to reddit. For
    reddit.com it is 2. Any function decorated with this will be forced to
    delay api_request_delay seconds from the calling of the last function
    decorated with this before executing.
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
    """Limit the number of chars in a function that outputs a string."""
    def function_limiter(function):
        @wraps(function)
        def function_wrapper(self, *args, **kwargs):
            output_string = function(self, *args, **kwargs)
            if len(output_string) > num_chars:
                output_string = output_string[:num_chars - 3] + '...'
            return output_string
        return function_wrapper
    return function_limiter


def parse_api_json_response(function):  # pylint: disable-msg=R0912
    """Raise client side exception(s) if errors in the API request response."""
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
    """Ensure the user has logged in."""
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
    """Ensure the user is a moderator of the subreddit."""
    @wraps(function)
    def moderator_required_function(self, *args, **kwargs):
        if isinstance(self, RedditContentObject):
            subreddit = self.subreddit
            user = self.reddit_session.user
        else:
            subreddit = args[0]
            user = self.user
        if not user.is_mod:
            raise errors.ModeratorRequired('%r is not moderator' %
                                           six.text_type(user))

        # pylint: disable-msg=W0212
        if user._mod_subs is None:
            user._mod_subs = {'mod': user.reddit_session.get_subreddit('mod')}
            for sub in user.my_moderation(limit=None):
                user._mod_subs[six.text_type(sub).lower()] = sub

        # Allow for multireddits
        for sub in six.text_type(subreddit).lower().split('+'):
            if sub not in user._mod_subs:
                raise errors.ModeratorRequired('%r is not a moderator of %r' %
                                               (six.text_type(user), sub))
        return function(self, *args, **kwargs)
    return moderator_required_function


# Avoid circular import: http://effbot.org/zone/import-confusion.htm
from .objects import RedditContentObject
from .helpers import _request
