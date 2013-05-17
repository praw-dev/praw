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

Mainly do two things. Ensure API guidelines are met and prevent unnecessary
failed API requests by testing that the call can be made first. Also limit the
length of output strings and parse json response for certain errors.
"""

import os
import six
import sys
from functools import wraps
from requests.compat import urljoin
from praw import errors


# Don't decorate functions when building the documentation
IS_SPHINX_BUILD = bool(os.getenv('SPHINX_BUILD'))


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


def raise_api_exceptions(function):
    """Raise client side exception(s) when present in the API response.

    Returned data is not modified.

    """
    @wraps(function)
    def wrapped(reddit_session, *args, **kwargs):
        return_value = function(reddit_session, *args, **kwargs)
        if isinstance(return_value, dict):
            if return_value.get('error') == 304:  # Not modified exception
                raise errors.NotModified(return_value)
            elif return_value.get('errors'):
                error_list = []
                for error_type, msg, value in return_value['errors']:
                    if error_type in errors.ERROR_MAPPING:
                        if error_type == 'RATELIMIT':
                            reddit_session.evict(args[0])
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
    """Return a decorator for methods that require captchas."""
    def get_captcha(reddit_session, captcha_id):
        """Prompt user for captcha solution and return a prepared result."""
        url = urljoin(reddit_session.config['captcha'],
                      captcha_id + '.png')
        sys.stdout.write('Captcha URL: %s\nCaptcha: ' % url)
        sys.stdout.flush()
        raw = sys.stdin.readline()
        if not raw:  # stdin has reached the end of file
            # Trigger exception raising next time through. The request is
            # cached so this will not require and extra request and delay.
            sys.stdin.close()
            return None
        return {'iden': captcha_id, 'captcha': raw.strip()}

    function.__doc__ += ('\nThis function may result in a captcha challenge. '
                         'PRAW will automatically prompt you for a response. '
                         'See :ref:`handling-captchas` if you want to manually'
                         ' handle captchas.')

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
                if raise_captcha_exception or \
                        not hasattr(sys.stdin, 'closed') or sys.stdin.closed:
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
      * are called upon a subreddit object (Subreddit RedditContentObject)
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
