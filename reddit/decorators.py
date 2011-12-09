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

import time
import warnings
from functools import wraps
from urlparse import urljoin

from reddit import errors


class RequireCaptcha(object):
    """Decorator for methods that require captchas."""

    def __init__(self, func):
        wraps(func)(self)
        self.func = func
        self.captcha_id = None
        self.captcha = None

    def __get__(self, obj, key):
        if obj is None:
            return self
        return self.__class__(self.func.__get__(obj, key))

    def __call__(self, *args, **kwargs):
        do_captcha = False
        while True:
            try:
                if do_captcha:
                    self.get_captcha()
                    kwargs['captcha'] = self.captcha_as_dict
                return self.func(*args, **kwargs)
            except errors.BadCaptcha:
                do_captcha = True

    @property
    def captcha_as_dict(self):
        return {'iden': self.captcha_id, 'captcha': self.captcha}

    def get_captcha(self):
        caller = self.func.im_self
        # This doesn't support the api_type:json parameter yet
        data = caller.request_json(caller.config['new_captcha'],
                                   {'renderstyle': 'html'})
        self.captcha_id = data['jquery'][-1][-1][-1]
        url = urljoin(caller.config['captcha'], self.captcha_id + '.png')
        print 'Captcha URL: ' + url
        self.captcha = raw_input('Captcha: ')


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


def parse_api_json_response(func):  # pylint: disable-msg=R0912
    """Decorator to look at the Reddit API response to an API POST request like
    vote, subscribe, login, etc. Basically, it just looks for certain errors in
    the return string. If it doesn't find one, then it just returns True.
    """
    @wraps(func)
    def error_checked_func(self, *args, **kwargs):
        return_value = func(self, *args, **kwargs)
        if isinstance(return_value, dict):
            for k in return_value:
                allowed = ('data', 'errors', 'kind', 'names', 'next', 'prev',
                           'users')
                if k not in allowed:
                    # The only jquery response we want to allow is captcha
                    if k == 'jquery' and return_value[k][-2][-1] == 'captcha':
                        continue
                    warnings.warn('Unknown return value key: %s' % k)
            if 'errors' in return_value and return_value['errors']:
                error_list = []
                for error_type, msg, value in return_value['errors']:
                    if error_type in errors.ERROR_MAPPING:
                        error_class = errors.ERROR_MAPPING[error_type]
                    else:
                        error_class = errors.APIException
                    error_list.append(error_class(error_type, msg, value))
                if len(error_list) == 1:
                    raise error_list[0]
                else:
                    raise errors.ExceptionList(error_list)
        return return_value
    return error_checked_func

# Avoid circular import: http://effbot.org/zone/import-confusion.htm
from reddit.objects import RedditContentObject
