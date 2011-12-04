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

from urlparse import urljoin

from base_objects import RedditContentObject
from features import Voteable, Deletable
from util import limit_chars


class Comment(Deletable, Voteable):
    """A class for comments."""

    kind = 't1'

    def __init__(self, reddit_session, json_dict):
        super(Comment, self).__init__(reddit_session, None, json_dict)
        if self.replies:
            self.replies = self.replies['data']['children']
            for reply in self.replies:
                reply.parent = self
        else:
            self.replies = []
        self.parent = None
        self.submission = None

    @limit_chars()
    def __str__(self):
        return getattr(self, 'body', '[Unloaded Comment]').encode('utf8')

    @property
    def is_root(self):
        return hasattr(self, 'parent')

    @property
    def permalink(self):
        return urljoin(self.submission.permalink, self.id)

    def _update_submission(self, submission):
        """Submission isn't set on __init__ thus we need to update it."""
        self.submission = submission
        for reply in self.replies:
            reply._update_submission(submission)

    def reply(self, text):
        """Reply to the comment with the specified text."""
        return self.reddit_session._add_comment(self.content_id, text)

    def mark_read(self):
        """ Marks the comment as read """
        return self.reddit_session._mark_as_read([self.content_id])


class MoreComments(RedditContentObject):
    """A class indicating there are more comments."""

    kind = 'more'

    def __init__(self, reddit_session, json_dict):
        super(MoreComments, self).__init__(reddit_session, None, json_dict)

    def _update_submission(self, _):
        pass

    def __str__(self):
        return '[More Comments]'.encode('utf8')

    @property
    def comments(self):
        url = urljoin(self.parent.submission.permalink, self.parent.id)
        submission_info, comment_info = self.reddit_session._request_json(url)
        comments = comment_info['data']['children']

        # We need to return the children of the parent as we already have
        # the parent
        assert(len(comments) == 1)
        return comments[0].replies
