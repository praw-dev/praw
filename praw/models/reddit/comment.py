"""Provide the Comment class."""
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from ...exceptions import ClientException
from ..comment_forest import CommentForest
from .base import RedditBase
from .mixins import InboxableMixin, ThingModerationMixin, UserContentMixin
from .redditor import Redditor


class Comment(RedditBase, InboxableMixin, UserContentMixin):
    """A class that represents a reddit comments."""

    STR_FIELD = 'id'

    @property
    def is_root(self):
        """Return True when the comment is a top level comment."""
        parent_type = self.parent_id.split('_', 1)[0]
        return parent_type == self._reddit.config.kinds['submission']

    @property
    def mod(self):
        """An instance of :class:`.CommentModeration`."""
        if self._mod is None:
            self._mod = CommentModeration(self)
        return self._mod

    @property
    def replies(self):
        """An instance of :class:`.CommentForest`."""
        if isinstance(self._replies, list):
            self._replies = CommentForest(self.submission, self._replies)
        return self._replies

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
        assert self.name not in submission._comments_by_id
        submission._comments_by_id[self.name] = self
        self._submission = submission
        for reply in getattr(self, 'replies', []):
            reply.submission = submission

    def __init__(self, reddit, id=None,  # pylint: disable=redefined-builtin
                 _data=None):
        """Construct an instance of the Comment object."""
        if bool(id) == bool(_data):
            raise TypeError('Either `id` or `_data` must be provided.')
        self._mod = self._replies = self._submission = None
        super(Comment, self).__init__(reddit, _data)
        if id:
            self.id = id  # pylint: disable=invalid-name
        else:
            self._fetched = True

    def __setattr__(self, attribute, value):
        """Objectify author, replies, and subreddit."""
        # pylint: disable=redefined-variable-type
        if attribute == 'author':
            value = Redditor.from_data(self._reddit, value)
        elif attribute == 'replies':
            if value == '':
                value = []
            else:
                value = self._reddit._objector.objectify(value).children
            attribute = '_replies'
        elif attribute == 'subreddit':
            value = self._reddit.subreddit(value)
        super(Comment, self).__setattr__(attribute, value)

    def parent(self):
        """Return the parent of the comment.

        The returned parent will be an instance of either
        :class:`.Comment`, or :class:`.Submission`.

        If this comment was obtained through a :class:`.Submission`, then its
        entire ancestry should be immediately available, requiring no extra
        network requests. However, if this comment was obtained through other
        means, e.g., ``reddit.comment('COMMENT_ID')``, or
        ``reddit.inbox.comment_replies``, then the returned parent may be a
        lazy instance of either :class:`.Comment`, or :class:`.Submission`.

        Lazy Comment Example:

        .. code:: python

           comment = reddit.comment('cklhv0f')
           parent = comment.parent()
           # `replies` is empty until the comment is refreshed
           print(parent.replies)  # Output: []
           parent.refresh()
           print(parent.replies)  # Output is at least: [Comment(id='cklhv0f')]

        """
        # pylint: disable=no-member
        if self.parent_id == self.submission.fullname:
            return self.submission

        if '_comments' in self.submission.__dict__ \
           and self.parent_id in self.submission._comments_by_id:
            # The Comment already exists, so simply return it
            return self.submission._comments_by_id[self.parent_id]
        # pylint: enable=no-member

        parent = Comment(self._reddit, self.parent_id.split('_', 1)[1])
        parent._submission = self.submission
        return parent

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

        If using :meth:`.Reddit.comment` this method must be called in order to
        obtain the comment's replies.

        """
        if 'context' in self.__dict__:  # Using hasattr triggers a fetch
            comment_path = self.context.split('?', 1)[0]
        else:
            comment_path = '{}_/{}'.format(
                self.submission._info_path(),  # pylint: disable=no-member
                self.id)
        comment_list = self._reddit.get(comment_path)[1].children
        if not comment_list:
            raise ClientException('Comment has been deleted')
        comment = comment_list[0]
        for reply in comment._replies:
            reply.submission = self.submission
        del comment.__dict__['_submission']  # Don't replace
        self.__dict__.update(comment.__dict__)
        return self


class CommentModeration(ThingModerationMixin):
    """Provide a set of functions pertaining to Comment moderation."""

    def __init__(self, comment):
        """Create a CommentModeration instance.

        :param comment: The comment to moderate.

        """
        self.thing = comment
