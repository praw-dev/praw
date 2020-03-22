"""Provide the Modmail class."""

from ....const import API_PATH
from ..modmail import ModmailConversation


class Modmail:
    """Provides modmail functions for a subreddit.

    For example, to send a new modmail from the subreddit ``r/test`` to user
    ``u/spez`` with the subject ``test`` along with a message body of
    ``hello``:

    .. code-block:: python

        reddit.subreddit('test').modmail.create('test', 'hello', 'spez')

    """

    def __call__(self, id=None, mark_read=False):  # noqa: D207, D301
        """Return an individual conversation.

        :param id: A reddit base36 conversation ID, e.g., ``2gmz``.
        :param mark_read: If True, conversation is marked as read
            (default: False).

        For example:

        .. code-block:: python

           reddit.subreddit('redditdev').modmail('2gmz', mark_read=True)

        To print all messages from a conversation as Markdown source:

        .. code-block:: python

           conversation = reddit.subreddit('redditdev').modmail('2gmz', \
mark_read=True)
           for message in conversation.messages:
               print(message.body_markdown)

        ``ModmailConversation.user`` is a special instance of
        :class:`.Redditor` with extra attributes describing the non-moderator
        user's recent posts, comments, and modmail messages within the
        subreddit, as well as information on active bans and mutes. This
        attribute does not exist on internal moderator discussions.

        For example, to print the user's ban status:

        .. code-block:: python

           conversation = reddit.subreddit('redditdev').modmail('2gmz', \
mark_read=True)
           print(conversation.user.ban_status)

        To print a list of recent submissions by the user:

        .. code-block:: python

           conversation = reddit.subreddit('redditdev').modmail('2gmz', \
mark_read=True)
           print(conversation.user.recent_posts)

        """
        # pylint: disable=invalid-name,redefined-builtin
        return ModmailConversation(
            self.subreddit._reddit, id=id, mark_read=mark_read
        )

    def __init__(self, subreddit):
        """Construct an instance of the Modmail object."""
        self.subreddit = subreddit

    def _build_subreddit_list(self, other_subreddits):
        """Return a comma-separated list of subreddit display names."""
        subreddits = [self.subreddit] + (other_subreddits or [])
        return ",".join(str(subreddit) for subreddit in subreddits)

    def bulk_read(self, other_subreddits=None, state=None):
        """Mark conversations for subreddit(s) as read.

        Due to server-side restrictions, 'all' is not a valid subreddit for
        this method. Instead, use :meth:`~.Modmail.subreddits` to get a list of
        subreddits using the new modmail.

        :param other_subreddits: A list of :class:`.Subreddit` instances for
            which to mark conversations (default: None).
        :param state: Can be one of: all, archived, highlighted, inprogress,
            mod, new, notifications, (default: all). "all" does not include
            internal or archived conversations.
        :returns: A list of :class:`.ModmailConversation` instances that were
            marked read.

        For example, to mark all notifications for a subreddit as read:

        .. code-block:: python

           subreddit = reddit.subreddit('redditdev')
           subreddit.modmail.bulk_read(state='notifications')

        """
        params = {"entity": self._build_subreddit_list(other_subreddits)}
        if state:
            params["state"] = state
        response = self.subreddit._reddit.post(
            API_PATH["modmail_bulk_read"], params=params
        )
        return [
            self(conversation_id)
            for conversation_id in response["conversation_ids"]
        ]

    def conversations(
        self,
        after=None,
        limit=None,
        other_subreddits=None,
        sort=None,
        state=None,
    ):  # noqa: D207, D301
        """Generate :class:`.ModmailConversation` objects for subreddit(s).

        :param after: A base36 modmail conversation id. When provided, the
            listing begins after this conversation (default: None).
        :param limit: The maximum number of conversations to fetch. If None,
            the server-side default is 25 at the time of writing
            (default: None).
        :param other_subreddits: A list of :class:`.Subreddit` instances for
            which to fetch conversations (default: None).
        :param sort: Can be one of: mod, recent, unread, user
            (default: recent).
        :param state: Can be one of: all, archived, highlighted, inprogress,
            mod, new, notifications, (default: all). "all" does not include
            internal or archived conversations.


        For example:

        .. code-block:: python

            conversations = reddit.subreddit('all').modmail.conversations(\
state='mod')

        """
        params = {}
        if self.subreddit != "all":
            params["entity"] = self._build_subreddit_list(other_subreddits)

        for name, value in {
            "after": after,
            "limit": limit,
            "sort": sort,
            "state": state,
        }.items():
            if value:
                params[name] = value

        response = self.subreddit._reddit.get(
            API_PATH["modmail_conversations"], params=params
        )
        for conversation_id in response["conversationIds"]:
            data = {
                "conversation": response["conversations"][conversation_id],
                "messages": response["messages"],
            }
            yield ModmailConversation.parse(
                data, self.subreddit._reddit, convert_objects=False
            )

    def create(self, subject, body, recipient, author_hidden=False):
        """Create a new modmail conversation.

        :param subject: The message subject. Cannot be empty.
        :param body: The message body. Cannot be empty.
        :param recipient: The recipient; a username or an instance of
            :class:`.Redditor`.
        :param author_hidden: When True, author is hidden from non-moderators
            (default: False).
        :returns: A :class:`.ModmailConversation` object for the newly created
            conversation.

        .. code-block:: python

           subreddit = reddit.subreddit('redditdev')
           redditor = reddit.redditor('bboe')
           subreddit.modmail.create('Subject', 'Body', redditor)

        """
        data = {
            "body": body,
            "isAuthorHidden": author_hidden,
            "srName": self.subreddit,
            "subject": subject,
            "to": recipient,
        }
        return self.subreddit._reddit.post(
            API_PATH["modmail_conversations"], data=data
        )

    def subreddits(self):
        """Yield subreddits using the new modmail that the user moderates.

        For example:

        .. code-block:: python

           subreddits = reddit.subreddit('all').modmail.subreddits()

        """
        response = self.subreddit._reddit.get(API_PATH["modmail_subreddits"])
        for value in response["subreddits"].values():
            subreddit = self.subreddit._reddit.subreddit(value["display_name"])
            subreddit.last_updated = value["lastUpdated"]
            yield subreddit

    def unread_count(self):
        """Return unread conversation count by conversation state.

        At time of writing, possible states are: archived, highlighted,
        inprogress, mod, new, notifications.

        :returns: A dict mapping conversation states to unread counts.

        For example, to print the count of unread moderator discussions:

        .. code-block:: python

           subreddit = reddit.subreddit('redditdev')
           unread_counts = subreddit.modmail.unread_count()
           print(unread_counts['mod'])

        """
        return self.subreddit._reddit.get(API_PATH["modmail_unread_count"])
