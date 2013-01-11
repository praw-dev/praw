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
    def error_checked_function(cls, *args, **kwargs):
        return_value = function(cls, *args, **kwargs)
        if isinstance(return_value, dict):
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


def restrict_access(scope, mod=False, login=False, oauth_only=False):
    """Restrict function access unless the user has the necessary permissions.

    Raises one of the following exceptions when appropriate:
      * LoginRequired
      * LoginOrOAuthRequired
        * the scope attribute will provide the necessary scope name
      * ModeratorRequired
      * ModeratorOrOAuthRequired
        * the scope attribute will provide the necessary scope name

    :param scope: Indicate the scope that is required for the API call. None or
        False must be passed to indicate that no scope handles the API call.
        All scopes eimply login=True. Scopes with 'mod' in their name imply
        mod=True.
    :param mod: Indicate that a moderator is required. Implies login=True.
    :param login: Indicate that a login is required.
    :param oauth_only: Indicate that only OAuth is supported for the function.

    Returned data is not modified.

    This decorator assumes that all mod required functions fit one of:

      * have the subreddit as the first argument (Reddit instance functions)
      * are called upon a subreddit object (Subredit RedditContentObject)
      * are called upon a RedditContent object with attribute subreddit

    """

    if not scope and oauth_only:
        raise TypeError('`scope` must be set when `oauth_only` is set')

    mod = mod or scope and 'mod' in scope
    login = login or mod or scope

    login_exceptions = ('flair_list',)
    moderator_exceptions = ('create_subreddit',)

    def wrap(function):
        @wraps(function)
        def wrapped(cls, *args, **kwargs):
            def mods_all():
                mod_subs = obj.user.get_cached_moderated_reddits()
                for sub in six.text_type(subreddit).lower().split('+'):
                    if sub not in mod_subs:
                        return False
                return True

            # This segment of code uses hasattr to determine what instance type
            # the function was called on. We could use isinstance if we wanted
            # to import the types at runtime (decorators is used by all the
            # types).
            if hasattr(cls, 'reddit_session'):
                obj = cls.reddit_session
                if mod:
                    if hasattr(cls, 'display_name'):  # Subreddit object
                        subreddit = cls
                    else:
                        subreddit = cls.subreddit  # Other RedditContentObject
                else:
                    subreddit = None
            else:
                obj = cls
                subreddit = args[0] if mod else None

            # This function sets _use_oauth for one time use only.
            # Verify that statement is actually true.
            assert not obj._use_oauth  # pylint: disable-msg=W0212

            if scope and obj.has_scope(scope):
                obj._use_oauth = True  # pylint: disable-msg=W0212
            elif oauth_only:
                raise errors.OAuthScopeRequired(function.__name__, scope)
            elif obj.is_logged_in():
                if not mod or mod and obj.user.is_mod and mods_all():
                    pass
                elif function.__name__ not in moderator_exceptions:
                    if scope:
                        raise errors.ModeratorOrScopeRequired(
                            function.__name__, scope)
                    else:
                        raise errors.ModeratorRequired(function.__name__)
            elif function.__name__ not in login_exceptions:
                if scope:
                    raise errors.LoginOrScopeRequired(function.__name__, scope)
                raise errors.LoginRequired(function.__name__)
            try:
                return function(cls, *args, **kwargs)
            finally:
                obj._use_oauth = False  # pylint: disable-msg=W0212
        return wrapped
    return wrap


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
            raise errors.OAuthAppRequired(err_msg)
        return function(self, *args, **kwargs)
    return validate_function


# Avoid circular import: http://effbot.org/zone/import-confusion.htm
from .helpers import _request
