"""Provide the Comment class."""
from six import string_types

from ...exceptions import ClientException
from ..comment_forest import CommentForest
from .base import RedditBase
from .mixins import InboxableMixin, ThingModerationMixin, UserContentMixin
from .redditor import Redditor
from .subreddit import Subreddit


class Comment(InboxableMixin, UserContentMixin, RedditBase):
    """A class that represents a reddit comments.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``author``              Provides an instance of :class:`.Redditor`.
    ``body``                The body of the comment.
    ``created_utc``         Time the comment was created, represented in
                            `Unix Time`_.
    ``distinguished``       Whether or not the comment is distinguished.
    ``edited``              Whether or not the comment has been edited.
    ``id``                  The ID of the comment.
    ``is_submitter``        Whether or not the comment author is also the
                            author of the submission.
    ``link_id``             The submission ID that the comment belongs to.
    ``parent_id``           The ID of the parent comment. If it is a top-level
                            comment, this returns the submission ID instead
                            (prefixed with 't3').
    ``permalink``           A permalink for the comment.
    ``replies``             Provides an instance of :class:`.CommentForest`.
    ``score``               The number of upvotes for the comment.
    ``stickied``            Whether or not the comment is stickied.
    ``submission``          Provides an instance of :class:`.Submission`. The
                            submission that the comment belongs to.
    ``subreddit``           Provides an instance of :class:`.Subreddit`. The
                            subreddit that the comment belongs to.
    ``subreddit_id``        The subreddit ID that the comment belongs to.
    ======================= ===================================================


    .. _Unix Time: https://en.wikipedia.org/wiki/Unix_time

    """

    MISSING_COMMENT_MESSAGE = ('This comment does not appear to be in the '
                               'comment tree')

    @staticmethod
    def id_from_url(url):
        """Get the ID of a comment from the full URL."""
        parts = RedditBase._url_parts(url)
        try:
            comment_index = parts.index("comments")
        except ValueError:
            raise ClientException("Invalid URL: {}".format(url))

        if len(parts) - 4 != comment_index:
            raise ClientException("Invalid URL: {}".format(url))
        return parts[-1]

    @classmethod
    def _objectify_acknowledged(cls, reddit, data):
        key = 'author'
        item = data.get(key)
        if isinstance(item, string_types):
            data[key] = (None
                         if item == '[deleted]' else
                         Redditor(reddit, name=item))
        elif isinstance(item, Redditor):
            item._reddit = reddit

        key = 'replies'
        item = data.get(key)
        if isinstance(item, (string_types, dict)):
            data[key] = ([]
                         if item == '' else
                         reddit._objector.objectify(item)._data['children'])

        key = 'subreddit'
        item = data.get(key)
        if isinstance(item, string_types):
            data[key] = Subreddit(reddit, display_name=item)
        elif isinstance(item, Subreddit):
            item._reddit = reddit

    @property
    def is_root(self):
        """Return True when the comment is a top level comment."""
        parent_type = self.parent_id.split("_", 1)[0]
        return parent_type == self._reddit.config.kinds["submission"]

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

        Sort order and reply limit can be set with the ``reply_sort`` and
        ``reply_limit`` attributes before replies are fetched, including
        any call to :meth:`.refresh`:

        .. code:: python

           comment.reply_sort = 'new'
           comment.refresh()
           replies = comment.replies

        """
        if isinstance(self._replies, list):
            self._replies = CommentForest(self.submission, self._replies)
        return self._replies

    @property
    def submission(self):
        """Return the Submission object this comment belongs to."""
        if not self._submission:  # Comment not from submission
            self._submission = self._reddit.submission(
                self._extract_submission_id()
            )
        return self._submission

    @submission.setter
    def submission(self, submission):
        """Update the Submission associated with the Comment."""
        submission._comments_by_id[self.name] = self
        self._submission = submission
        for reply in self.replies:
            reply.submission = submission

    def __init__(
        self,
        reddit,
        id=None,  # pylint: disable=redefined-builtin
        url=None,
        _data=None,
    ):
        """Construct an instance of the Comment object."""
        if [id, url, _data].count(None) != 2:
            raise TypeError('Exactly one of `id`, `url`, or `_data` must be '
                            'provided.')

        self._mod = None
        self._replies = None
        self._submission = None

        init_by_data = False
        if _data is None:
            _data = {}
            if id is not None:
                _data['id'] = id
            elif url is not None:
                _data['id'] = self.id_from_url(url)
        else:
            init_by_data = True
            self._objectify_acknowledged(reddit, _data)
            self._replies = _data.pop('replies', None)

        super(Comment, self).__init__(reddit, _data=_data)

        if init_by_data:
            self._fetched = True

        self.reply_limit = None
        self.reply_sort = None

    def _extract_submission_id(self):
        if 'context' in self._data:
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

        parent = Comment(self._reddit, self.parent_id.split("_", 1)[1])
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
        if 'context' in self._data:
            comment_path = self.context.split('?', 1)[0]
        else:
            comment_path = '{}_/{}'.format(
                self.submission._info_path(),
                self.id)

        # The context limit appears to be 8, but let's ask for more anyway.
        params = {'context': 100}
        if self.reply_limit:
            params['limit'] = self.reply_limit
        if self.reply_sort:
            params['sort'] = self.reply_sort
        comment_list = self._reddit.get(comment_path,
                                        params=params)[1].children
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

        self._replies = comment._replies
        self._data.update(comment._data)

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

    REMOVAL_MESSAGE_API = "removal_comment_message"

    def __init__(self, comment):
        """Create a CommentModeration instance.

        :param comment: The comment to moderate.

        """
        self.thing = comment
