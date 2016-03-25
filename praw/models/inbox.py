"""Provide the Front class."""
from ..const import API_PATH
from .listing.generator import ListingGenerator
from .base import PRAWBase


class Inbox(PRAWBase):
    """Inbox is a Listing class that represents the Inbox."""

    def all(self, **generator_kwargs):
        """Return a ListingGenerator for all inbox comments and messages.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, API_PATH['inbox'],
                                **generator_kwargs)

    def comment_replies(self, **generator_kwargs):
        """Return a ListingGenerator for comment replies.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

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

    def messages(self, **generator_kwargs):
        """Return a ListingGenerator for inbox messages.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, API_PATH['messages'],
                                **generator_kwargs)

    def submission_replies(self, **generator_kwargs):
        """Return a ListingGenerator for submission replies.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, API_PATH['submission_replies'],
                                **generator_kwargs)

    def sent(self, **generator_kwargs):
        """Return a ListingGenerator for sent messages.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, API_PATH['sent'],
                                **generator_kwargs)

    def unread(self, mark_read=False, **generator_kwargs):
        """Return a ListingGenerator for unread comments and messages.

        :param mark_read: Marks the messages as read when they're obtained
            (Default: False).

        Note: When marking messages as read, the entire batch (up to 100 at a
        time) is marked as read when fetched. Failure to consume the entire
        listing may result in missed messages if you only obtain unread
        messages.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        params = {'mark': mark_read}
        return ListingGenerator(self._reddit, API_PATH['unread'],
                                params=params, **generator_kwargs)
