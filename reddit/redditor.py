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

from base_objects import RedditContentObject
from helpers import _get_section
from util import limit_chars
from decorators import require_login
from settings import DEFAULT_CONTENT_LIMIT
from urls import urls

class Redditor(RedditContentObject):
    """A class for Redditor methods."""

    kind = "t2"

    get_overview = _get_section("/")
    get_comments = _get_section("/comments")
    get_submitted = _get_section("/submitted")

    def __init__(self, reddit_session, user_name=None, json_dict=None,
                 fetch=True):
        self.user_name = user_name
        # Store the urls we will need internally
        self.URL = urls["redditor_page"] % self.user_name
        self.ABOUT_URL = urls["redditor_about_page"] % self.user_name

        super(Redditor, self).__init__(reddit_session, user_name, json_dict,
                                       fetch)

    # overriding base class _get_json_dict because url is different.
    # ideally this would be abstracted, but this is a bandaid for an
    # existing problem. should rewrite a lot of this in the future.
    def _get_json_dict(self):
        response = self._request_json(self.ABOUT_URL, as_objects=False)
        json_dict = response.get("data")
        return json_dict

    @limit_chars()
    def __str__(self):
        """Have the str just be the user's name"""
        return self.user_name.encode("utf8")

    @require_login
    def get_my_reddits(self, limit=DEFAULT_CONTENT_LIMIT):
        """Return all of the current user's subreddits."""
        return self.reddit_session._get_content(urls["my_reddits"], limit=limit)

    @require_login
    def get_my_moderation(self, limit=DEFAULT_CONTENT_LIMIT):
        """Return all of the current user's subreddits that they moderate."""
        return self.reddit_session._get_content(urls["my_moderation"], limit=limit)

    @require_login
    def friend(self):
        self.reddit_session._friend(self.user_name)

    @require_login
    def unfriend(self):
        self.reddit_session._unfriend(self.user_name)

