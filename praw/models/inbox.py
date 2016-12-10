"""Provide the Front class."""
from ..const import API_PATH
from .listing.generator import ListingGenerator
from .base import PRAWBase


class Inbox(PRAWBase):
    """Inbox is a Listing class that represents the Inbox."""

    def all(self, **generator_kwargs):
        """Return a ListingGenerator for all inbox comments and messages.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(self._reddit, API_PATH['inbox'],
                                **generator_kwargs)

    def comment_replies(self, **generator_kwargs):
        """Return a ListingGenerator for comment replies.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(self._reddit, API_PATH['comment_replies'],
                                **generator_kwargs)

    def mark_read(self, items):
        """Mark Comments or Messages as read.

        :param items: A list containing Comments and Messages to be be marked
            as read relative to the authenticated user's inbox.

        Requests are batched at 25 items (reddit limit).

        """
        while items:
            data = {'id': ','.join(x.fullname for x in items[:25])}
            self._reddit.post(API_PATH['read_message'], data=data)
            items = items[25:]

    def mark_unread(self, items):
        """Unmark Comments or Messages as read.

        :param items: A list containing Comments and Messages to be be marked
            as unread relative to the authenticated user's inbox.

        Requests are batched at 25 items (reddit limit).

        """
        while items:
            data = {'id': ','.join(x.fullname for x in items[:25])}
            self._reddit.post(API_PATH['unread_message'], data=data)
            items = items[25:]

    def mentions(self, **generator_kwargs):
        """Return a ListingGenerator for mentions.

        A mention is :class:`.Comment` in which the authorized redditor is
        named in its body like ``/u/redditor_name``.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(self._reddit, API_PATH['mentions'],
                                **generator_kwargs)

    def message(self, message_id):
        """Return a Message corresponding to ``message_id``.

        :param message_id: The base36 id of a message.

        """
        listing = self._reddit.get(API_PATH['message'].format(id=message_id))
        messages = [listing[0]] + list(self._reddit._objector
                                       .objectify(listing[0].replies))
        while messages:
            message = messages.pop(0)
            if message.id == message_id:
                return message

    def messages(self, **generator_kwargs):
        """Return a ListingGenerator for inbox messages.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(self._reddit, API_PATH['messages'],
                                **generator_kwargs)

    def submission_replies(self, **generator_kwargs):
        """Return a ListingGenerator for submission replies.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(self._reddit, API_PATH['submission_replies'],
                                **generator_kwargs)

    def sent(self, **generator_kwargs):
        """Return a ListingGenerator for sent messages.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(self._reddit, API_PATH['sent'],
                                **generator_kwargs)

    def unread(self, mark_read=False, **generator_kwargs):
        """Return a ListingGenerator for unread comments and messages.

        :param mark_read: Marks the messages as read when they're obtained
            (Default: False).

        .. note:: When marking messages as read, the entire batch (up to 100 at
                  a time) is marked as read when fetched. Failure to consume
                  the entire listing may result in missed messages if you only
                  obtain unread messages.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        params = {'mark': mark_read}
        return ListingGenerator(self._reddit, API_PATH['unread'],
                                params=params, **generator_kwargs)
