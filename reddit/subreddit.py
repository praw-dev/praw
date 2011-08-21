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
from helpers import _modify_relationship, _get_sorter
from util import limit_chars
from urls import urls

class Subreddit(RedditContentObject):
    """A class for Subreddits."""

    kind = "t5"

    ban = _modify_relationship("banned")
    make_contributor = _modify_relationship("contributor")
    make_moderator = _modify_relationship("moderator")

    unban = _modify_relationship("banned", unlink=True)
    remove_contributor = _modify_relationship("contributor", unlink=True)
    remove_moderator = _modify_relationship("moderator", unlink=True)

    ban.__doc__ = "Ban the target user."
    make_contributor.__doc__ = \
       "Make the target user a contributor in the given subreddit."
    make_moderator.__doc__ = \
       "Make the target user a moderator in the given subreddit."

    unban.__doc__ = "Unban the target user."
    remove_contributor.__doc__ = \
       "Remove the target user from contributor status in the given subreddit."
    remove_moderator.__doc__ = \
       "Revoke the target user's moderator privileges in the given subreddit."

    get_hot = _get_sorter("/")
    get_controversial = _get_sorter("/controversial", time="day")
    get_new = _get_sorter("/new", sort="rising")
    get_top = _get_sorter("/top", time="day")
    get_new_by_date = _get_sorter("/new", sort="new")
    get_new_by_date.__doc__ = \
        "Fetch new stories by submission date, rather than by 'rising'"

    def __init__(self, reddit_session, subreddit_name=None, json_dict=None,
                 fetch=False):
        self.URL = urls["subreddit_page"] % subreddit_name
        self.ABOUT_URL = urls["subreddit_about_page"] % subreddit_name

        self.display_name = subreddit_name
        super(Subreddit, self).__init__(reddit_session, subreddit_name,
                                        json_dict, fetch)

    @limit_chars()
    def __str__(self):
        """Just display the subreddit name."""
        return self.display_name.encode("utf8")

    def submit(self, *args, **kwargs):
        """
        Submit a new link.
        """
        return self.reddit_session.submit(self, *args, **kwargs)

    def subscribe(self):
        """If logged in, subscribe to the given subreddit."""
        return self.reddit_session._subscribe(self.name)

    def unsubscribe(self):
        """If logged in, unsubscribe from the given subreddit."""
        return self.reddit_session._subscribe(self.name,
                                              unsubscribe=True)

