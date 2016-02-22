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

They mainly do two things: ensure API guidelines are followed and
prevent unnecessary failed API requests by testing that the call can be made
first. Also, they can limit the length of output strings and parse json
response for certain errors.
"""

import decorator
import sys
from functools import wraps
from praw.decorator_helpers import (
    _get_captcha,
    _make_func_args
)
from praw import errors
from warnings import simplefilter, warn


# Enable deprecation warnings
simplefilter('default')


def alias_function(function, class_name):
    """Create a RedditContentObject function mapped to a BaseReddit function.

    The BaseReddit classes define the majority of the API's functions. The
    first argument for many of these functions is the RedditContentObject that
    they operate on. This factory returns functions appropriate to be called on
    a RedditContent object that maps to the corresponding BaseReddit function.

    """
    @wraps(function)
    def wrapped(self, *args, **kwargs):
        func_args = _make_func_args(function)
        if 'subreddit' in func_args and func_args.index('subreddit') != 1:
            # Only happens for search
            kwargs['subreddit'] = self
            return function(self.reddit_session, *args, **kwargs)
        else:
            return function(self.reddit_session, self, *args, **kwargs)
    # Only grab the short-line doc and add a link to the complete doc
    if wrapped.__doc__ is not None:
        wrapped.__doc__ = wrapped.__doc__.split('\n', 1)[0]
        wrapped.__doc__ += ('\n\nSee :meth:`.{0}.{1}` for complete usage. '
                            'Note that you should exclude the subreddit '
                            'parameter when calling this convenience method.'
                            .format(class_name, function.__name__))
    # Don't hide from sphinx as this is a parameter modifying decorator
    return wrapped


def deprecated(msg=''):
    """Deprecate decorated method."""
    @decorator.decorator
    def wrap(function, *args, **kwargs):
        if not kwargs.pop('disable_warning', False):
            warn(msg, DeprecationWarning)
        return function(*args, **kwargs)
    return wrap


@decorator.decorator
def limit_chars(function, *args, **kwargs):
    """Truncate the string returned from a function and return the result."""
    output_chars_limit = args[0].reddit_session.config.output_chars_limit
    output_string = function(*args, **kwargs)
    if -1 < output_chars_limit < len(output_string):
        output_string = output_string[:output_chars_limit - 3] + '...'
    return output_string


@decorator.decorator
def oauth_generator(function, *args, **kwargs):
    """Set the _use_oauth keyword argument to True when appropriate.

    This is needed because generator functions may be called at anytime, and
    PRAW relies on the Reddit._use_oauth value at original call time to know
    when to make OAuth requests.

    Returned data is not modified.

    """
    if getattr(args[0], '_use_oauth', False):
        kwargs['_use_oauth'] = True
    return function(*args, **kwargs)


@decorator.decorator
def raise_api_exceptions(function, *args, **kwargs):
    """Raise client side exception(s) when present in the API response.

    Returned data is not modified.

    """
    try:
        return_value = function(*args, **kwargs)
    except errors.HTTPException as exc:
        if exc._raw.status_code != 400:  # pylint: disable=W0212
            raise  # Unhandled HTTPErrors
        try:  # Attempt to convert v1 errors into older format (for now)
            data = exc._raw.json()  # pylint: disable=W0212
            assert len(data) == 2
            return_value = {'errors': [(data['reason'],
                                        data['explanation'], '')]}
        except Exception:
            raise exc
    if isinstance(return_value, dict):
        if return_value.get('error') == 304:  # Not modified exception
            raise errors.NotModified(return_value)
        elif return_value.get('errors'):
            error_list = []
            for error_type, msg, value in return_value['errors']:
                if error_type in errors.ERROR_MAPPING:
                    if error_type == 'RATELIMIT':
                        args[0].evict(args[1])
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


@decorator.decorator
def require_captcha(function, *args, **kwargs):
    """Return a decorator for methods that require captchas."""
    raise_captcha_exception = kwargs.pop('raise_captcha_exception', False)
    captcha_id = None

    # Get a handle to the reddit session
    if hasattr(args[0], 'reddit_session'):
        reddit_session = args[0].reddit_session
    else:
        reddit_session = args[0]

    while True:
        try:
            if captcha_id:
                captcha_answer = _get_captcha(reddit_session, captcha_id)

                # When the method is being decorated, all of its default
                # parameters become part of this *args tuple. This means that
                # *args currently contains a None where the captcha answer
                # needs to go. If we put the captcha in the **kwargs,
                # we get a TypeError for having two values of the same param.
                func_args = _make_func_args(function)
                if 'captcha' in func_args:
                    captcha_index = func_args.index('captcha')
                    args = list(args)
                    args[captcha_index] = captcha_answer
                else:
                    kwargs['captcha'] = captcha_answer
            return function(*args, **kwargs)
        except errors.InvalidCaptcha as exception:
            if raise_captcha_exception or \
                    not hasattr(sys.stdin, 'closed') or sys.stdin.closed:
                raise
            captcha_id = exception.response['captcha']


@decorator.decorator
def require_oauth(function, *args, **kwargs):
    """Verify that the OAuth functions can be used prior to use.

    Returned data is not modified.

    """
    if not args[0].has_oauth_app_info:
        err_msg = ("The OAuth app config parameters client_id, client_secret "
                   "and redirect_url must be specified to use this function.")
        raise errors.OAuthAppRequired(err_msg)
    return function(*args, **kwargs)
