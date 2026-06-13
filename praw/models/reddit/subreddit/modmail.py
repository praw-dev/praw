"""Provide the Modmail class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from praw.const import API_PATH
from praw.models.listing.generator import ListingGenerator
from praw.models.reddit.base import RedditBase
from praw.models.reddit.modmail import ModmailConversation

if TYPE_CHECKING:
    from collections.abc import Iterator

    from praw import models


class Modmail:
    """Provides modmail functions for a :class:`.Subreddit`.

    For example, to send a new modmail from r/test to u/spez with the subject ``"test"``
    along with a message body of ``"hello"``:

    .. code-block:: python

        reddit.subreddit("test").modmail.create(subject="test", body="hello", recipient="spez")

    """

    def __call__(self, id: str | None = None, *, mark_read: bool = False) -> ModmailConversation:
        """Return an individual conversation.

        :param id: A reddit base36 conversation ID, e.g., ``"2gmz"``.
        :param mark_read: If ``True``, conversation is marked as read (default:
            ``False``).

        For example:

        .. code-block:: python

            reddit.subreddit("test").modmail("2gmz", mark_read=True)

        To print all messages from a conversation as Markdown source:

        .. code-block:: python

            conversation = reddit.subreddit("test").modmail("2gmz", mark_read=True)
            for message in conversation.messages:
                print(message.body_markdown)

        ``ModmailConversation.user`` is a special instance of :class:`.Redditor` with
        extra attributes describing the non-moderator user's recent posts, comments, and
        modmail messages within the subreddit, as well as information on active bans and
        mutes. This attribute does not exist on internal moderator discussions.

        For example, to print the user's ban status:

        .. code-block:: python

            conversation = reddit.subreddit("test").modmail("2gmz", mark_read=True)
            print(conversation.user.ban_status)

        To print a list of recent submissions by the user:

        .. code-block:: python

            conversation = reddit.subreddit("test").modmail("2gmz", mark_read=True)
            print(conversation.user.recent_posts)

        """
        return ModmailConversation(self.subreddit._reddit, id=id, mark_read=mark_read)

    def __init__(self, subreddit: models.Subreddit) -> None:
        """Initialize a :class:`.Modmail` instance."""
        self.subreddit = subreddit

    def _build_subreddit_list(self, other_subreddits: list[models.Subreddit | str] | None) -> str:
        """Return a comma-separated list of subreddit display names."""
        subreddits = [self.subreddit] + (other_subreddits or [])
        return ",".join(str(subreddit) for subreddit in subreddits)

    def bulk_read(
        self,
        *,
        other_subreddits: list[models.Subreddit | str] | None = None,
        state: str | None = None,
    ) -> list[ModmailConversation]:
        """Mark conversations for subreddit(s) as read.

        .. note::

            Due to server-side restrictions, r/all is not a valid subreddit for this
            method. Instead, use :meth:`~.Modmail.subreddits` to get a list of
            subreddits using the new modmail.

        :param other_subreddits: A list of :class:`.Subreddit` instances for which to
            mark conversations (default: ``None``).
        :param state: Can be one of: ``"all"``, ``"archived"``, or ``"highlighted"``,
            ``"inprogress"``, ``"join_requests"``, ``"mod"``, ``"new"``,
            ``"notifications"``, or ``"appeals"`` (default: ``"all"``). ``"all"`` does
            not include internal, archived, or appeals conversations.

        :returns: A list of :class:`.ModmailConversation` instances that were marked
            read.

        For example, to mark all notifications for a subreddit as read:

        .. code-block:: python

            subreddit = reddit.subreddit("test")
            subreddit.modmail.bulk_read(state="notifications")

        """
        params: dict[str, str | int] = {"entity": self._build_subreddit_list(other_subreddits)}
        if state:
            params["state"] = state
        response = self.subreddit._reddit.post(API_PATH["modmail_bulk_read"], params=params)
        return [self(conversation_id) for conversation_id in response["conversation_ids"]]

    def conversations(
        self,
        *,
        other_subreddits: list[models.Subreddit | str] | None = None,
        sort: str | None = None,
        state: str | None = None,
        **generator_kwargs: Any,
    ) -> Iterator[ModmailConversation]:
        """Generate :class:`.ModmailConversation` objects for subreddit(s).

        :param other_subreddits: A list of :class:`.Subreddit` instances for which to
            fetch conversations (default: ``None``).
        :param sort: Can be one of: ``"mod"``, ``"recent"``, ``"unread"``, or ``"user"``
            (default: ``"recent"``).
        :param state: Can be one of: ``"all"``, ``"archived"``, ``"highlighted"``,
            ``"inprogress"``, ``"join_requests"``, ``"mod"``, ``"new"``,
            ``"notifications"``, or ``"appeals"`` (default: ``"all"``). ``"all"`` does
            not include internal, archived, or appeals conversations.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        For example:

        .. code-block:: python

            conversations = reddit.subreddit("all").modmail.conversations(state="mod")

        """
        params = {}
        if self.subreddit != "all":
            params["entity"] = self._build_subreddit_list(other_subreddits)
        RedditBase._safely_add_arguments(arguments=generator_kwargs, key="params", sort=sort, state=state, **params)
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["modmail_conversations"],
            **generator_kwargs,
        )

    def create(
        self,
        *,
        author_hidden: bool = False,
        body: str,
        recipient: str | models.Redditor,
        subject: str,
    ) -> ModmailConversation:
        """Create a new :class:`.ModmailConversation`.

        :param author_hidden: When ``True``, author is hidden from non-moderators
            (default: ``False``).
        :param body: The message body. Cannot be empty.
        :param recipient: The recipient; a username or an instance of
            :class:`.Redditor`.
        :param subject: The message subject. Cannot be empty.

        :returns: A :class:`.ModmailConversation` object for the newly created
            conversation.

        .. code-block:: python

            subreddit = reddit.subreddit("test")
            redditor = reddit.redditor("bboe")
            subreddit.modmail.create(subject="Subject", body="Body", recipient=redditor)

        """
        data = {
            "body": body,
            "isAuthorHidden": author_hidden,
            "srName": self.subreddit,
            "subject": subject,
            "to": recipient,
        }
        return self.subreddit._reddit.post(API_PATH["modmail_conversations"], data=data)

    def subreddits(self) -> Iterator[models.Subreddit]:
        """Yield subreddits using the new modmail that the user moderates.

        For example:

        .. code-block:: python

            subreddits = reddit.subreddit("all").modmail.subreddits()

        """
        response = self.subreddit._reddit.get(API_PATH["modmail_subreddits"])
        for value in response["subreddits"].values():
            subreddit = self.subreddit._reddit.subreddit(value["display_name"])
            subreddit.last_updated = value["lastUpdated"]
            yield subreddit

    def unread_count(self) -> dict[str, int]:
        """Return unread conversation count by conversation state.

        At time of writing, possible states are: ``"archived"``, ``"highlighted"``,
        ``"inprogress"``, ``"join_requests"``, ``"mod"``, ``"new"``,
        ``"notifications"``, or ``"appeals"``.

        :returns: A dict mapping conversation states to unread counts.

        For example, to print the count of unread moderator discussions:

        .. code-block:: python

            subreddit = reddit.subreddit("test")
            unread_counts = subreddit.modmail.unread_count()
            print(unread_counts["mod"])

        """
        return self.subreddit._reddit.get(API_PATH["modmail_unread_count"])
