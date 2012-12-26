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

Includes two main execeptions. ClientException, when something goes
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


class LoginRequired(ClientException):
    """
    Raised when a user is not logged in for a privileged call.

    This exception is raised on a preemtive basis, whereas NotLoggedIn occurs
    in response to a lack of credientials on a priviliged API call.
    """


class ModeratorRequired(ClientException):
    """Raised when a logged in user is not a moderator for the subreddit."""


class APIException(Exception):
    """Base exception class for the reddit API bindings."""
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
    """Raised when more than one exception occured."""
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


class InvalidCaptcha(APIException):
    """An exception for when an incorrect captcha error is returned."""
    ERROR_TYPE = 'BAD_CAPTCHA'


class InvalidEmails(APIException):
    """An exception for when invalid emails are provided."""
    ERROR_TYPE = 'BAD_EMAILS'


class InvalidFlairTarget(APIException):
    """An exception raised when an invalid user is passed as a flair target."""
    ERROR_TYPE = 'BAD_FLAIR_TARGET'


class InvalidUser(APIException):
    """An exception for when a user doesn't exist."""
    ERROR_TYPE = 'USER_DOESNT_EXIST'


class InvalidUserPass(APIException):
    """An exception for failed logins."""
    ERROR_TYPE = 'WRONG_PASSWORD'


class NotLoggedIn(APIException):
    """An exception for when a Reddit user isn't logged in."""
    ERROR_TYPE = 'USER_REQUIRED'


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
