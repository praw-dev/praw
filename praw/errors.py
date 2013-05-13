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
Error classes

Includes two main exceptions. ClientException, when something goes
wrong on our end and APIExeception for when something goes wrong on the
server side. A number of classes extend these two main exceptions for more
specific exceptions.
"""

import inspect
import six
import sys


class ClientException(Exception):

    """Base exception class for errors that don't involve the remote API."""

    def __init__(self, message):
        super(ClientException, self).__init__()
        self.message = message

    def __str__(self):
        return self.message


class InvalidSubreddit(ClientException):

    """Indicates that an invalid subreddit name was supplied."""


class OAuthScopeRequired(ClientException):

    """Indicates that an OAuth2 scope is required to make the function call.

    The attribute `scope` will contain the name of the necessary scope.

    """

    def __init__(self, function, scope, message=None):
        if not message:
            message = '`{0}` requires the OAuth2 scope `{1}`'.format(function,
                                                                     scope)
        super(OAuthScopeRequired, self).__init__(message)
        self.scope = scope


class LoginRequired(ClientException):

    """Indicates that a logged in session is required.

    This exception is raised on a preemptive basis, whereas NotLoggedIn occurs
    in response to a lack of credentials on a privileged API call.

    """

    def __init__(self, function, message=None):
        if not message:
            message = '`{0}` requires a logged in session'.format(function)
        super(LoginRequired, self).__init__(message)


class LoginOrScopeRequired(OAuthScopeRequired, LoginRequired):

    """Indicates that either a logged in session or OAuth2 scope is required.

    The attribute `scope` will contain the name of the necessary scope.

    """

    def __init__(self, function, scope, message=None):
        if not message:
            message = ('`{0}` requires a logged in session or the '
                       'OAuth2 scope `{1}`').format(function, scope)
        super(LoginOrScopeRequired, self).__init__(function, scope, message)


class ModeratorRequired(LoginRequired):

    """Indicates that a moderator of the subreddit is required."""

    def __init__(self, function):
        msg = '`{0}` requires a moderator of the subreddit'.format(function)
        super(ModeratorRequired, self).__init__(msg)


class ModeratorOrScopeRequired(LoginOrScopeRequired, ModeratorRequired):

    """Indicates that a moderator of the sub or OAuth2 scope is required.

    The attribute `scope` will contain the name of the necessary scope.

    """

    def __init__(self, function, scope):
        message = ('`{0}` requires a moderator of the subreddit or the '
                   'OAuth2 scope `{1}`').format(function, scope)
        super(ModeratorOrScopeRequired, self).__init__(function, scope,
                                                       message)


class OAuthAppRequired(ClientException):

    """Raised when an OAuth client cannot be initialized.

    This occurs when any one of the OAuth config values are not set.

    """


class RedirectException(ClientException):

    """Raised when a redirect response occurs that is not expected."""

    def __init__(self, request_url, response_url):
        super(RedirectException, self).__init__(
            'Unexpected redirect from {0} to {1}'
            .format(request_url, response_url))
        self.request_url = request_url
        self.response_url = response_url


class OAuthException(Exception):

    """Base exception class for OAuth API calls.

    Attribute `message` contains the error message.
    Attribute `url` contains the url that resulted in the error.

    """

    def __init__(self, message, url):
        super(OAuthException, self).__init__()
        self.message = message
        self.url = url

    def __str__(self):
        return self.message + " on url {0}".format(self.url)


class OAuthInsufficientScope(OAuthException):

    """Raised when the current OAuth scope is not sufficient for the action.

    This indicates the access token is valid, but not for the desired action.

    """


class OAuthInvalidGrant(OAuthException):

    """Raised when the code to retrieve access information is not valid."""


class OAuthInvalidToken(OAuthException):

    """Raised when the current OAuth access token is not valid."""


class APIException(Exception):

    """Base exception class for the reddit API error message exceptions."""

    def __init__(self, error_type, message, field='', response=None):
        super(APIException, self).__init__()
        self.error_type = error_type
        self.message = message
        self.field = field
        self.response = response

    def __str__(self):
        if hasattr(self, 'ERROR_TYPE'):
            return '`%s` on field `%s`' % (self.message, self.field)
        else:
            return '(%s) `%s` on field `%s`' % (self.error_type, self.message,
                                                self.field)


class ExceptionList(APIException):

    """Raised when more than one exception occurred."""

    def __init__(self, errors):
        super(ExceptionList, self).__init__(None, None)
        self.errors = errors

    def __str__(self):
        ret = '\n'
        for i, error in enumerate(self.errors):
            ret += '\tError %d) %s\n' % (i, six.text_type(error))
        return ret


class AlreadySubmitted(APIException):

    """An exception to indicate that a URL was previously submitted."""

    ERROR_TYPE = 'ALREADY_SUB'


class AlreadyModerator(APIException):

    """Used to indicate that a user is already a moderator of a subreddit."""

    ERROR_TYPE = 'ALREADY_MODERATOR'


class InvalidCaptcha(APIException):

    """An exception for when an incorrect captcha error is returned."""

    ERROR_TYPE = 'BAD_CAPTCHA'


class InvalidEmails(APIException):

    """An exception for when invalid emails are provided."""

    ERROR_TYPE = 'BAD_EMAILS'


class InvalidFlairTarget(APIException):

    """An exception raised when an invalid user is passed as a flair target."""

    ERROR_TYPE = 'BAD_FLAIR_TARGET'


class InvalidInvite(APIException):

    """Raised when attempting to accept a nonexistent moderator invite."""

    ERROR_TYPE = 'NO_INVITE_FOUND'


class InvalidUser(APIException):

    """An exception for when a user doesn't exist."""

    ERROR_TYPE = 'USER_DOESNT_EXIST'


class InvalidUserPass(APIException):

    """An exception for failed logins."""

    ERROR_TYPE = 'WRONG_PASSWORD'


class NotLoggedIn(APIException):

    """An exception for when a Reddit user isn't logged in."""

    ERROR_TYPE = 'USER_REQUIRED'


class NotModified(APIException):

    """An exception raised when reddit returns {'error': 304}.

    This error indicates that the requested content was not modified and is
    being requested too frequently. Such an error usually occurs when multiple
    instances of PRAW are running concurrently or in rapid succession.

    """

    def __init__(self, response):
        super(NotModified, self).__init__(None, None, response=response)

    def __str__(self):
        return 'That page has not been modified.'


class SubredditExists(APIException):

    """An exception to indicate that a subreddit name is not available."""

    ERROR_TYPE = 'SUBREDDIT_EXISTS'


class RateLimitExceeded(APIException):

    """An exception for when something has happened too frequently."""

    ERROR_TYPE = 'RATELIMIT'

    def __init__(self, error_type, message, field='', response=None):
        super(RateLimitExceeded, self).__init__(error_type, message,
                                                field, response)
        self.sleep_time = self.response['ratelimit']


class UsernameExists(APIException):

    """An exception to indicate that a username is not available."""

    ERROR_TYPE = 'USERNAME_TAKEN'


def _build_error_mapping():
    tmp = {}
    predicate = lambda x: inspect.isclass(x) and hasattr(x, 'ERROR_TYPE')
    for _, obj in inspect.getmembers(sys.modules[__name__], predicate):
        tmp[obj.ERROR_TYPE] = obj
    return tmp
ERROR_MAPPING = _build_error_mapping()
