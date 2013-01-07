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
        """Return url after stripping trailing .json and trailing slashes."""
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

    def __call__(self, reddit_session, url, *args, **kwargs):
        # Ignore uploads
        if kwargs.get('files'):
            return self.function(reddit_session, url, *args, **kwargs)

        normalized_url = self.normalize_url(url)
        key = (reddit_session, normalized_url, repr(args),
               frozenset(six.iteritems(kwargs)))
        call_time = time.time()
        self.clear_timeouts(call_time, reddit_session.config.cache_timeout)
        self._timeouts.setdefault(key, call_time)
        if key in self._cache:
            return self._cache[key]
        result = self.function(reddit_session, url, *args, **kwargs)
        if kwargs.get('raw_response'):
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
        """Prompt user for captcha solution and return a prepared result."""
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
            except errors.InvalidCaptcha as exception:
                captcha_id = exception.response['captcha']


class SleepAfter(object):  # pylint: disable-msg=R0903

    """Ensure frequency of API calls doesn't exceed guidelines.

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


def alias_function(function):
    """Create a RedditContentObject function mapped to a BaseReddit function.

    The BaseReddit classes define the majority of the API's functions. The
    first argument for many of these functions is the RedditContentObject that
    they operate on. This factory returns functions appropriate to be called on
    a RedditContent object that maps to the corresponding BaseReddit function.

    """
    @wraps(function)
    def wrapped(self, *args, **kwargs):
        return function(self.reddit_session, self, *args, **kwargs)
    return wrapped


def limit_chars(function):
    """Truncate the string returned from a function and return the result."""
    @wraps(function)
    def function_wrapper(self, *args, **kwargs):
        output_chars_limit = self.reddit_session.config.output_chars_limit
        output_string = function(self, *args, **kwargs)
        if -1 < output_chars_limit < len(output_string):
            output_string = output_string[:output_chars_limit - 3] + '...'
        return output_string
    return function_wrapper


def parse_api_json_response(function):  # pylint: disable-msg=R0912
    """Raise client side exception(s) when presenet in the API response.

    Returned data is not modified.

    """
    @wraps(function)
    def error_checked_function(self, *args, **kwargs):
        return_value = function(self, *args, **kwargs)
        allowed = ('captcha', 'data', 'error', 'errors', 'kind', 'names',
                   'next', 'prev', 'ratelimit', 'users')
        if isinstance(return_value, dict):
            for key in return_value:
                if key not in allowed:
                    warnings.warn_explicit('Unknown return key: %s' % key,
                                           UserWarning, '', 0)
            if return_value.get('error') == 304:  # Not modified exception
                raise errors.NotModified(return_value)
            elif return_value.get('errors'):
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
    """Verify user is logged in prior to making the API request.

    Returned data is not modified.

    """
    @wraps(function)
    def login_required_function(self, *args, **kwargs):
        from praw.objects import RedditContentObject
        if isinstance(self, RedditContentObject):
            user = self.reddit_session.user
            modhash = self.reddit_session.modhash
            access_token = self.reddit_session.access_token
        else:
            user = self.user
            modhash = self.modhash
            access_token = self.access_token

        if access_token is None and (user is None or modhash is None):
            raise errors.LoginRequired('%r requires login' % function.__name__)
        else:
            return function(self, *args, **kwargs)
    return login_required_function


def require_moderator(function):
    """Verify the user is a moderator of the subreddit.

    The verification takes place prior to making the API request.

    Returned data is not modified.

    """
    @wraps(function)
    def moderator_required_function(self, *args, **kwargs):
        from praw.objects import RedditContentObject
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


def require_oauth(function):
    """Verify that the OAuth functions can be used prior to use.

    Returned data is not modified.

    """
    @wraps(function)
    def validate_function(self, *args, **kwargs):
        if not self.has_oauth_app_info:
            err_msg = ("The OAuth app config parameters client_id, "
                       "client_secret and redirect_url must be specified to "
                       "use this function.")
            raise errors.OAuthRequired(err_msg)
        return function(self, *args, **kwargs)
    return validate_function


# Avoid circular import: http://effbot.org/zone/import-confusion.htm
from .helpers import _request
