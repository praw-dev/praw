"""Provide the Front class."""
from ..const import API_PATH
from .listing.generator import ListingGenerator
from .base import PRAWBase
from .util import stream_generator


class Inbox(PRAWBase):
    """Inbox is a Listing class that represents the Inbox."""

    def all(self, **generator_kwargs):
        """Return a ListingGenerator for all inbox comments and messages.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To output the type and ID of all items available via this listing do:

        .. code:: python

           for item in reddit.inbox.all(limit=None):
               print(repr(item))

        """
        return ListingGenerator(
            self._reddit, API_PATH["inbox"], **generator_kwargs
        )

    def collapse(self, items):
        """Mark an inbox message as collapsed.

        :param items: A list containing instances of :class:`.Message`.

        Requests are batched at 25 items (reddit limit).

        For example, to collapse all unread Messages, try:

        .. code:: python

            from praw.models import Message
            unread_messages = []
            for item in reddit.inbox.unread(limit=None):
                if isinstance(item, Message):
                    unread_messages.append(item)
            reddit.inbox.collapse(unread_messages)

        .. seealso::

           :meth:`.Message.uncollapse`

        """
        while items:
            data = {"id": ",".join(x.fullname for x in items[:25])}
            self._reddit.post(API_PATH["collapse"], data=data)
            items = items[25:]

    def comment_replies(self, **generator_kwargs):
        """Return a ListingGenerator for comment replies.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To output the author of one request worth of comment replies try:

        .. code:: python

           for reply in reddit.inbox.comment_replies():
               print(reply.author)

        """
        return ListingGenerator(
            self._reddit, API_PATH["comment_replies"], **generator_kwargs
        )

    def mark_read(self, items):
        """Mark Comments or Messages as read.

        :param items: A list containing instances of :class:`.Comment` and/or
            :class:`.Message` to be be marked as read relative to the
            authorized user's inbox.

        Requests are batched at 25 items (reddit limit).

        For example, to mark all unread Messages as read, try:

        .. code:: python

            from praw.models import Message
            unread_messages = []
            for item in reddit.inbox.unread(limit=None):
                if isinstance(item, Message):
                    unread_messages.append(item)
            reddit.inbox.mark_read(unread_messages)

        .. seealso::

           :meth:`.Comment.mark_read` and :meth:`.Message.mark_read`

        """
        while items:
            data = {"id": ",".join(x.fullname for x in items[:25])}
            self._reddit.post(API_PATH["read_message"], data=data)
            items = items[25:]

    def mark_unread(self, items):
        """Unmark Comments or Messages as read.

        :param items: A list containing instances of :class:`.Comment` and/or
            :class:`.Message` to be be marked as unread relative to the
            authorized user's inbox.

        Requests are batched at 25 items (reddit limit).

        For example, to mark the first 10 items as unread try:

        .. code:: python

            to_unread = list(reddit.inbox.all(limit=10))
            reddit.inbox.mark_unread(to_unread)

        .. seealso::

           :meth:`.Comment.mark_unread` and :meth:`.Message.mark_unread`

        """
        while items:
            data = {"id": ",".join(x.fullname for x in items[:25])}
            self._reddit.post(API_PATH["unread_message"], data=data)
            items = items[25:]

    def mentions(self, **generator_kwargs):
        r"""Return a ListingGenerator for mentions.

        A mention is :class:`.Comment` in which the authorized redditor is
        named in its body like ``/u/redditor_name``.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        For example, to output the author and body of the first 25 mentions
        try:

        .. code:: python

           for mention in reddit.inbox.mentions(limit=25):
               print('{}\n{}\n'.format(mention.author, mention.body))

        """
        return ListingGenerator(
            self._reddit, API_PATH["mentions"], **generator_kwargs
        )

    def message(self, message_id):
        """Return a Message corresponding to ``message_id``.

        :param message_id: The base36 id of a message.

        Example:

        .. code:: python

           message = reddit.inbox.message('7bnlgu')

        """
        listing = self._reddit.get(API_PATH["message"].format(id=message_id))
        messages = [listing[0]] + listing[0].replies
        while messages:
            message = messages.pop(0)
            if message.id == message_id:
                return message

    def messages(self, **generator_kwargs):
        """Return a ListingGenerator for inbox messages.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        For example, to output the subject of the most recent 5 messages try:

        .. code:: python

           for message in reddit.inbox.messages(limit=5):
               print(message.subject)

        """
        return ListingGenerator(
            self._reddit, API_PATH["messages"], **generator_kwargs
        )

    def sent(self, **generator_kwargs):
        """Return a ListingGenerator for sent messages.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        For example, to output the recipient of the most recent 15 messages
        try:

        .. code:: python

           for message in reddit.inbox.sent(limit=15):
               print(message.dest)

        """
        return ListingGenerator(
            self._reddit, API_PATH["sent"], **generator_kwargs
        )

    def stream(self, **stream_options):
        """Yield new inbox items as they become available.

        Items are yielded oldest first. Up to 100 historical items will
        initially be returned.

        Keyword arguments are passed to :func:`.stream_generator`.

        For example, to retrieve all new inbox items, try:

        .. code:: python

           for item in reddit.inbox.stream():
               print(item)

        """
        return stream_generator(self.unread, **stream_options)

    def submission_replies(self, **generator_kwargs):
        """Return a ListingGenerator for submission replies.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To output the author of one request worth of submission replies try:

        .. code:: python

           for reply in reddit.inbox.submission_replies():
               print(reply.author)

        """
        return ListingGenerator(
            self._reddit, API_PATH["submission_replies"], **generator_kwargs
        )

    def uncollapse(self, items):
        """Mark an inbox message as uncollapsed.

        :param items: A list containing instances of :class:`.Message`.

        Requests are batched at 25 items (reddit limit).

        For example, to uncollapse all unread Messages, try:

        .. code:: python

            from praw.models import Message
            unread_messages = []
            for item in reddit.inbox.unread(limit=None):
                if isinstance(item, Message):
                    unread_messages.append(item)
            reddit.inbox.uncollapse(unread_messages)

        .. seealso::

           :meth:`.Message.collapse`

        """
        while items:
            data = {"id": ",".join(x.fullname for x in items[:25])}
            self._reddit.post(API_PATH["uncollapse"], data=data)
            items = items[25:]

    def unread(self, mark_read=False, **generator_kwargs):
        """Return a ListingGenerator for unread comments and messages.

        :param mark_read: Marks the inbox as read (default: False).

        .. note:: This only marks the inbox as read not the messages. Use
                  :meth:`.Inbox.mark_read` to mark the messages.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        For example, to output the author of unread comments try:

        .. code:: python

           from praw.models import Comment
           for item in reddit.inbox.unread(limit=None):
               if isinstance(item, Comment):
                   print(item.author)

        """
        self._safely_add_arguments(generator_kwargs, "params", mark=mark_read)
        return ListingGenerator(
            self._reddit, API_PATH["unread"], **generator_kwargs
        )
