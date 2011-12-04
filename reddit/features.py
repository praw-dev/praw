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
from decorators import require_login
from helpers import _request
from urls import urls


class Saveable(RedditContentObject):
    """
    Additional interface for Reddit content objects that can be saved.
    Currently only Submissions, but this may change at a later date, as
    eventually Comments will probably end up being saveable.
    """
    @require_login
    def save(self, unsave=False):
        """If logged in, save the content."""
        url = urls["unsave" if unsave else "save"]
        params = {'id': self.content_id,
                  'executed': "unsaved" if unsave else "saved",
                  'uh': self.reddit_session.modhash,
                  'api_type': 'json'}
        response = self.reddit_session._request_json(url, params)
        _request.is_stale(urls.saved_links)
        return response

    def unsave(self):
        return self.save(unsave=True)


class Deletable(RedditContentObject):
    """
    Additional Interface for Reddit content objects that can be deleted
    (currently Submission and Comment).
    """
    def delete(self):
        url = urls["del"]
        params = {'id': self.content_id,
                  'executed': 'deleted',
                  'uh': self.reddit_session.modhash,
                  'api_type': 'json'}
        response = self.reddit_session._request_json(url, params)
        _request.is_stale([urls["redditor_page"]])
        return response


class Voteable(RedditContentObject):
    """
    Additional interface for Reddit content objects that can be voted on
    (currently Submission and Comment).
    """
    @require_login
    def vote(self, direction=0):
        """
        Vote for the given item in the direction specified.
        """
        url = urls["vote"]
        params = {'id': self.content_id,
                  'dir': str(direction),
                  'uh': self.reddit_session.modhash,
                  'api_type': 'json'}
        return self.reddit_session._request_json(url, params)

    def upvote(self):
        return self.vote(direction=1)

    def downvote(self):
        return self.vote(direction=-1)

    def clear_vote(self):
        return self.vote()
