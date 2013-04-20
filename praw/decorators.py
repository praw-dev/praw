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

import os
import six
import sys
import time
from functools import wraps
from requests.compat import urljoin
from praw import errors


# Don't decorate functions when building the documentation
IS_SPHINX_BUILD = bool(os.getenv('SPHINX_BUILD'))


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

    def empty(self):
        """Empty the entire cache."""
        self._cache = {}
        self._timeouts = {}

    def evict(self, urls):
        """Remove cached RedditContentObject by URL."""
        urls = [self.normalize_url(url) for url in urls]
        relevant_caches = [key for key in self._cache if key[1] in urls]
        for key in relevant_caches:
            del self._cache[key]
            del self._timeouts[key]


def alias_function(function, class_name):
    """Create a RedditContentObject function mapped to a BaseReddit function.

    The BaseReddit classes define the majority of the API's functions. The
    first argument for many of these functions is the RedditContentObject that
    they operate on. This factory returns functions appropriate to be called on
    a RedditContent object that maps to the corresponding BaseReddit function.

    """
    @wraps(function)
    def wrapped(self, *args, **kwargs):
        return function(self.reddit_session, self, *args, **kwargs)
    # Only grab the short-line doc and add a link to the complete doc
    wrapped.__doc__ = wrapped.__doc__.split('\n', 1)[0]
    wrapped.__doc__ += ('\n\nSee :meth:`.{0}.{1}` for complete usage. '
                        'Note that you should exclude the first parameter '
                        'when calling this convenience method.'
                        .format(class_name, function.__name__))
    # Don't hide from sphinx as this is a parameter modifying decorator
    return wrapped


def limit_chars(function):
    """Truncate the string returned from a function and return the result."""
    @wraps(function)
    def wrapped(self, *args, **kwargs):
        output_chars_limit = self.reddit_session.config.output_chars_limit
        output_string = function(self, *args, **kwargs)
        if -1 < output_chars_limit < len(output_string):
            output_string = output_string[:output_chars_limit - 3] + '...'
        return output_string
    return function if IS_SPHINX_BUILD else wrapped


def oauth_generator(function):
    """Set the _use_oauth keyword argument to True when appropriate.

    This is needed because generator functions may be called at anytime, and
    PRAW relies on the Reddit._use_oauth value at original call time to know
    when to make OAuth requests.

    Returned data is not modified.

    """
    @wraps(function)
    def wrapped(reddit_session, *args, **kwargs):
        if getattr(reddit_session, '_use_oauth', False):
            kwargs['_use_oauth'] = True
        return function(reddit_session, *args, **kwargs)
    return function if IS_SPHINX_BUILD else wrapped


def parse_api_json_response(function):  # pylint: disable-msg=R0912
    """Raise client side exception(s) when presenet in the API response.

    Returned data is not modified.

    """
    @wraps(function)
    def wrapped(cls, *args, **kwargs):
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
    return function if IS_SPHINX_BUILD else wrapped


def require_captcha(function):
    """Decorator for methods that require captchas."""
    def get_captcha(reddit_session, captcha_id):
        """Prompt user for captcha solution and return a prepared result."""
        url = urljoin(reddit_session.config['captcha'],
                      captcha_id + '.png')
        sys.stdout.write('Captcha URL: %s\nCaptcha: ' % url)
        sys.stdout.flush()
        captcha = sys.stdin.readline().strip()
        return {'iden': captcha_id, 'captcha': captcha}

    @wraps(function)
    def wrapped(obj, *args, **kwargs):
        if 'raise_captcha_exception' in kwargs:
            raise_captcha_exception = kwargs['raise_captcha_exception']
            del kwargs['raise_captcha_exception']
        else:
            raise_captcha_exception = False
        captcha_id = None

        # Get a handle to the reddit session
        if hasattr(obj, 'reddit_session'):
            reddit_session = obj.reddit_session
        else:
            reddit_session = obj

        while True:
            try:
                if captcha_id:
                    kwargs['captcha'] = get_captcha(reddit_session, captcha_id)
                return function(obj, *args, **kwargs)
            except errors.InvalidCaptcha as exception:
                if raise_captcha_exception:
                    raise
                captcha_id = exception.response['captcha']
    return function if IS_SPHINX_BUILD else wrapped


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
        All scopes save for `read` imply login=True. Scopes with 'mod' in their
        name imply mod=True.
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
    login = login or mod or scope and scope != 'read'

    login_exceptions = ('get_flair_list',)
    moderator_exceptions = ('create_subreddit',)

    def wrap(function):
        @wraps(function)
        def wrapped(cls, *args, **kwargs):
            def is_mod_of_all(user, subreddit):
                mod_subs = user.get_cached_moderated_reddits()
                subs = six.text_type(subreddit).lower().split('+')
                return all(sub in mod_subs for sub in subs)

            login_req = login and function.__name__ not in login_exceptions
            mod_req = mod and function.__name__ not in moderator_exceptions

            # This segment of code uses hasattr to determine what instance type
            # the function was called on. We could use isinstance if we wanted
            # to import the types at runtime (decorators is used by all the
            # types).
            if cls is None:  # Occurs with (un)friend
                assert login_req
                raise errors.LoginRequired(function.__name__)
            elif hasattr(cls, 'reddit_session'):
                obj = cls.reddit_session
                if mod:
                    if hasattr(cls, 'display_name'):  # Subreddit object
                        subreddit = cls
                    else:
                        # Defer access until necessary for RedditContentObject.
                        # This is because scoped sessions may not require this
                        # attribute to exist, thus it might not be set.
                        subreddit = False
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
            elif login_req and obj.is_logged_in():
                if subreddit is False:
                    # Now fetch the subreddit attribute. There is no good
                    # reason for it to not be set during a logged in session.
                    subreddit = cls.subreddit
                if mod_req and not is_mod_of_all(obj.user, subreddit):
                    if scope:
                        raise errors.ModeratorOrScopeRequired(
                            function.__name__, scope)
                    raise errors.ModeratorRequired(function.__name__)
            elif login_req:
                if scope:
                    raise errors.LoginOrScopeRequired(function.__name__, scope)
                raise errors.LoginRequired(function.__name__)
            try:
                return function(cls, *args, **kwargs)
            finally:
                obj._use_oauth = False  # pylint: disable-msg=W0212
        return function if IS_SPHINX_BUILD else wrapped
    return wrap


def require_oauth(function):
    """Verify that the OAuth functions can be used prior to use.

    Returned data is not modified.

    """
    @wraps(function)
    def wrapped(self, *args, **kwargs):
        if not self.has_oauth_app_info:
            err_msg = ("The OAuth app config parameters client_id, "
                       "client_secret and redirect_url must be specified to "
                       "use this function.")
            raise errors.OAuthAppRequired(err_msg)
        return function(self, *args, **kwargs)
    return function if IS_SPHINX_BUILD else wrapped


def sleep_after(function):
    """Ensure frequency of API calls doesn't exceed guidelines.

    We are allowed to make a API request every api_request_delay seconds as
    specified in praw.ini. This value may differ from reddit to reddit. For
    reddit.com it is 2. Any function decorated with this will be forced to
    delay api_request_delay seconds from the calling of the last function
    decorated with this before executing.

    """
    @wraps(function)
    def wrapped(reddit_session, *args, **kwargs):
        config = reddit_session.config
        last = last_call.get(config.domain, 0)
        now = time.time()
        delay = last + int(config.api_request_delay) - now
        if delay > 0:
            now += delay
            time.sleep(delay)
        last_call[config.domain] = now
        return function(reddit_session, *args, **kwargs)
    last_call = {}
    return function if IS_SPHINX_BUILD else wrapped


# Avoid circular import: http://effbot.org/zone/import-confusion.htm
from .helpers import _request
