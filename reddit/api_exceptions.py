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

class APIException(Exception):
    """Base exception class for these API bindings."""
    pass

class APIWarning(UserWarning):
    """Base exception class for these API bindings."""
    pass

class BadCaptcha(APIException):
    """An exception for when an incorrect captcha error is returned."""
    def __str__(self):
        return "Incorrect captcha entered."

class NotLoggedInException(APIException):
    """An exception for when a Reddit user isn't logged in."""
    def __str__(self):
        return "You need to login to do that!"

class InvalidUserPass(APIException):
    """An exception for failed logins."""
    def __str__(self):
        return "Invalid username/password."
