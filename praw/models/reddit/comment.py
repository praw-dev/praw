"""Provide the Comment class."""
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from .base import RedditBase
from .mixins import InboxableMixin, UserContentMixin
from .redditor import Redditor
from ...exceptions import ClientException


class Comment(RedditBase, InboxableMixin, UserContentMixin):
    """A class that represents a reddit comments."""

    STR_FIELD = 'id'

    @property
    def is_root(self):
        """Return True when the comment is a top level comment."""
        parent_type = self.parent_id.split('_', 1)[0]
        return parent_type == self._reddit.config.kinds['submission']

    @property
    def submission(self):
        """Return the Submission object this comment belongs to."""
        if not self._submission:  # Comment not from submission
            self._submission = self._reddit.submission(
                self.link_id.split('_', 1)[1])
        return self._submission

    @submission.setter
    def submission(self, submission):
        """Update the Submission associated with the Comment."""
        assert self.name not in submission.comments._comments_by_id
        submission.comments._comments_by_id[self.name] = self
        self._submission = submission
        for reply in getattr(self, 'replies', []):
            reply.submission = submission

    def __init__(self, reddit, id=None,  # pylint: disable=redefined-builtin
                 _data=None):
        """Construct an instance of the Comment object."""
        if bool(id) == bool(_data):
            raise TypeError('Either `id` or `_data` must be provided.')
        super(Comment, self).__init__(reddit, _data)
        self._submission = None
        if id:
            self.id = id  # pylint: disable=invalid-name

    def __setattr__(self, attribute, value):
        """Objectify author, replies, and subreddit."""
        # pylint: disable=redefined-variable-type
        if attribute == 'author':
            value = Redditor.from_data(self._reddit, value)
        elif attribute == 'replies':
            # TODO: From info URL replies = "", even if there are replies.
            # From a comment tree replies = "" when it has no replies.
            if value == '':
                value = []
            else:
                value = self._reddit._objector.objectify(value).children
        elif attribute == 'subreddit':
            value = self._reddit.subreddit(value)
        super(Comment, self).__setattr__(attribute, value)

    def permalink(self, fast=False):
        """Return a permalink to the comment.

        :param fast: Return the result as quickly as possible (Default: False).

        In order to determine the full permalink for a comment, the Submission
        may need to be fetched if it hasn't been already. Set ``fast=True`` if
        you want to bypass that possible load.

        A full permalink looks like:
        /r/redditdev/comments/2gmzqe/praw_https_enabled/cklhv0f

        A fast-loaded permalink for the same comment will look like:
        /comments/2gmzqe//cklhv0f

        """
        # pylint: disable=no-member
        if not fast or 'permalink' in self.submission.__dict__:
            return urljoin(self.submission.permalink, self.id)
        return '/comments/{}//{}'.format(self.submission.id, self.id)

    def refresh(self):
        """Refresh the comment's attributes.

        If using ``Reddit.comment`` this method must be called in order to
        obtain the comment's replies.

        """
        comment_path = self.submission._info_path() + '_/{}'.format(self.id)
        comment_list = self._reddit.get(comment_path)[1].children
        if not comment_list:
            raise ClientException('Comment has been deleted')
        comment = comment_list[0]
        del comment.__dict__['_submission']  # Don't replace
        self.__dict__.update(comment.__dict__)
        return self
