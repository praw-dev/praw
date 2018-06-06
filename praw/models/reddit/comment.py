"""Provide the Comment class."""
from ...exceptions import ClientException
from ..comment_forest import CommentForest
from .base import RedditBase
from .mixins import InboxableMixin, ThingModerationMixin, UserContentMixin
from .redditor import Redditor


class Comment(RedditBase, InboxableMixin, UserContentMixin):
    """A class that represents a reddit comments."""

    MISSING_COMMENT_MESSAGE = ('This comment does not appear to be in the '
                               'comment tree')
    STR_FIELD = 'id'

    @staticmethod
    def id_from_url(url):
        """Get the ID of a comment from the full URL."""
        parts = RedditBase._url_parts(url)
        try:
            comment_index = parts.index('comments')
        except ValueError:
            raise ClientException('Invalid URL: {}'.format(url))

        if len(parts) - 4 != comment_index:
            raise ClientException('Invalid URL: {}'.format(url))
        return parts[-1]

    @property
    def is_root(self):
        """Return True when the comment is a top level comment."""
        parent_type = self.parent_id.split('_', 1)[0]
        return parent_type == self._reddit.config.kinds['submission']

    @property
    def mod(self):
        """Provide an instance of :class:`.CommentModeration`."""
        if self._mod is None:
            self._mod = CommentModeration(self)
        return self._mod

    @property
    def replies(self):
        """Provide an instance of :class:`.CommentForest`.

        This property may return an empty list if the comment
        has not been refreshed with :meth:`.refresh()`

        """
        if isinstance(self._replies, list):
            self._replies = CommentForest(self.submission, self._replies)
        return self._replies

    @property
    def submission(self):
        """Return the Submission object this comment belongs to."""
        if not self._submission:  # Comment not from submission
            self._submission = self._reddit.submission(
                self._extract_submission_id())
        return self._submission

    @submission.setter
    def submission(self, submission):
        """Update the Submission associated with the Comment."""
        submission._comments_by_id[self.name] = self
        self._submission = submission
        # pylint: disable=not-an-iterable
        for reply in getattr(self, 'replies', []):
            reply.submission = submission

    def __init__(self, reddit, id=None,  # pylint: disable=redefined-builtin
                 url=None, _data=None):
        """Construct an instance of the Comment object."""
        if [id, url, _data].count(None) != 2:
            raise TypeError('Exactly one of `id`, `url`, or `_data` must be '
                            'provided.')
        self._mod = self._replies = self._submission = None
        super(Comment, self).__init__(reddit, _data)
        if id:
            self.id = id  # pylint: disable=invalid-name
        elif url:
            self.id = self.id_from_url(url)
        else:
            self._fetched = True

    def __setattr__(self, attribute, value):
        """Objectify author, replies, and subreddit."""
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

    def _extract_submission_id(self):
        if 'context' in self.__dict__:
            return self.context.rsplit('/', 4)[1]
        return self.link_id.split('_', 1)[1]

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

        .. warning:: Successive calls to :meth:`.parent()` may result in a
           network request per call when the comment is not obtained through a
           :class:`.Submission`. See below for an example of how to minimize
           requests.

        If you have a deeply nested comment and wish to most efficiently
        discover its top-most :class:`.Comment` ancestor you can chain
        successive calls to :meth:`.parent()` with calls to :meth:`.refresh()`
        at every 9 levels. For example:

        .. code:: python

           comment = reddit.comment('dkk4qjd')
           ancestor = comment
           refresh_counter = 0
           while not ancestor.is_root:
               ancestor = ancestor.parent()
               if refresh_counter % 9 == 0:
                   ancestor.refresh()
               refresh_counter += 1
           print('Top-most Ancestor: {}'.format(ancestor))

        The above code should result in 5 network requests to Reddit. Without
        the calls to :meth:`.refresh()` it would make at least 31 network
        requests.

        """
        # pylint: disable=no-member
        if self.parent_id == self.submission.fullname:
            return self.submission

        if self.parent_id in self.submission._comments_by_id:
            # The Comment already exists, so simply return it
            return self.submission._comments_by_id[self.parent_id]
        # pylint: enable=no-member

        parent = Comment(self._reddit, self.parent_id.split('_', 1)[1])
        parent._submission = self.submission
        return parent

    def refresh(self):
        """Refresh the comment's attributes.

        If using :meth:`.Reddit.comment` this method must be called in order to
        obtain the comment's replies.

        Example usage:

        .. code:: python

           comment = reddit.comment('dkk4qjd')
           comment.refresh()

        """
        if 'context' in self.__dict__:  # Using hasattr triggers a fetch
            comment_path = self.context.split('?', 1)[0]
        else:
            comment_path = '{}_/{}'.format(
                self.submission._info_path(),  # pylint: disable=no-member
                self.id)

        # The context limit appears to be 8, but let's ask for more anyway.
        comment_list = self._reddit.get(comment_path,
                                        params={'context': 100})[1].children
        if not comment_list:
            raise ClientException(self.MISSING_COMMENT_MESSAGE)

        # With context, the comment may be nested so we have to find it
        comment = None
        queue = comment_list[:]
        while queue and (comment is None or comment.id != self.id):
            comment = queue.pop()
            if isinstance(comment, Comment):
                queue.extend(comment._replies)

        if comment.id != self.id:
            raise ClientException(self.MISSING_COMMENT_MESSAGE)

        if self._submission is not None:
            del comment.__dict__['_submission']  # Don't replace if set
        self.__dict__.update(comment.__dict__)

        for reply in comment_list:
            reply.submission = self.submission
        return self


class CommentModeration(ThingModerationMixin):
    """Provide a set of functions pertaining to Comment moderation.

    Example usage:

    .. code:: python

       comment = reddit.comment('dkk4qjd')
       comment.mod.approve()

    """

    def __init__(self, comment):
        """Create a CommentModeration instance.

        :param comment: The comment to moderate.

        """
        self.thing = comment
