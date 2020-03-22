"""Provide the SubredditModerationStream class."""

from ...util import stream_generator


class SubredditModerationStream:
    """Provides moderator streams."""

    def __init__(self, subreddit):
        """Create a SubredditModerationStream instance.

        :param subreddit: The moderated subreddit associated with the streams.

        """
        self.subreddit = subreddit

    def edited(self, only=None, **stream_options):
        """Yield edited comments and submissions as they become available.

        :param only: If specified, one of ``'comments'``, or ``'submissions'``
            to yield only results of that type.

        Keyword arguments are passed to :func:`.stream_generator`.

        For example, to retrieve all new edited submissions/comments made
        to all moderated subreddits, try:

        .. code-block:: python

           for item in reddit.subreddit('mod').mod.stream.edited():
               print(item)

        """
        return stream_generator(
            self.subreddit.mod.edited, only=only, **stream_options
        )

    def log(self, action=None, mod=None, **stream_options):
        """Yield moderator log entries as they become available.

        :param action: If given, only return log entries for the specified
            action.
        :param mod: If given, only return log entries for actions made by the
            passed in Redditor.

        For example, to retrieve all new mod actions made to all moderated
        subreddits, try:

        .. code-block:: python

           for log in reddit.subreddit('mod').mod.stream.log():
               print("Mod: {}, Subreddit: {}".format(log.mod, log.subreddit))

        """
        return stream_generator(
            self.subreddit.mod.log,
            action=action,
            mod=mod,
            attribute_name="id",
            **stream_options
        )

    def modmail_conversations(
        self, other_subreddits=None, sort=None, state=None, **stream_options
    ):
        """Yield unread new modmail messages as they become available.

        :param other_subreddits: A list of :class:`.Subreddit` instances for
            which to fetch conversations (default: None).
        :param sort: Can be one of: mod, recent, unread, user
            (default: recent).
        :param state: Can be one of: all, archived, highlighted, inprogress,
            mod, new, notifications, (default: all). "all" does not include
            internal or archived conversations.

        Keyword arguments are passed to :func:`.stream_generator`.

        To print new mail in the unread modmail queue try:

        .. code-block:: python

           for message in reddit.subreddit('all').mod.stream.modmail_conversations():
               print("From: {}, To: {}".format(message.owner, message.participant))

        """  # noqa: E501
        if self.subreddit == "mod":
            self.subreddit = self.subreddit._reddit.subreddit("all")
        return stream_generator(
            self.subreddit.modmail.conversations,
            other_subreddits=other_subreddits,
            sort=sort,
            state=state,
            attribute_name="id",
            exclude_before=True,
            **stream_options
        )

    def modqueue(self, only=None, **stream_options):
        """Yield comments/submissions in the modqueue as they become available.

        :param only: If specified, one of ``'comments'``, or ``'submissions'``
            to yield only results of that type.

        Keyword arguments are passed to :func:`.stream_generator`.

        To print all new modqueue items try:

        .. code-block:: python

           for item in reddit.subreddit('mod').mod.stream.modqueue():
               print(item)

        """
        return stream_generator(
            self.subreddit.mod.modqueue, only=only, **stream_options
        )

    def reports(self, only=None, **stream_options):
        """Yield reported comments and submissions as they become available.

        :param only: If specified, one of ``'comments'``, or ``'submissions'``
            to yield only results of that type.

        Keyword arguments are passed to :func:`.stream_generator`.

        To print new user and mod report reasons in the report queue try:

        .. code-block:: python

           for item in reddit.subreddit('mod').mod.stream.reports():
               print(item)

        """
        return stream_generator(
            self.subreddit.mod.reports, only=only, **stream_options
        )

    def spam(self, only=None, **stream_options):
        """Yield spam comments and submissions as they become available.

        :param only: If specified, one of ``'comments'``, or ``'submissions'``
            to yield only results of that type.

        Keyword arguments are passed to :func:`.stream_generator`.

        To print new items in the spam queue try:

        .. code-block:: python

           for item in reddit.subreddit('mod').mod.stream.spam():
               print(item)

        """
        return stream_generator(
            self.subreddit.mod.spam, only=only, **stream_options
        )

    def unmoderated(self, **stream_options):
        """Yield unmoderated submissions as they become available.

        Keyword arguments are passed to :func:`.stream_generator`.

        To print new items in the unmoderated queue try:

        .. code-block:: python

           for item in reddit.subreddit('mod').mod.stream.unmoderated():
               print(item)

        """
        return stream_generator(
            self.subreddit.mod.unmoderated, **stream_options
        )

    def unread(self, **stream_options):
        """Yield unread old modmail messages as they become available.

        Keyword arguments are passed to :func:`.stream_generator`.

        See ``inbox`` for all messages.

        To print new mail in the unread modmail queue try:

        .. code-block:: python

           for message in reddit.subreddit('mod').mod.stream.unread():
               print("From: {}, To: {}".format(message.author, message.dest))

        """
        return stream_generator(self.subreddit.mod.unread, **stream_options)
