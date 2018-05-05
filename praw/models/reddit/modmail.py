"""Provide models for new modmail."""
from ...const import API_PATH
from .base import RedditBase


class ModmailConversation(RedditBase):
    """A class for modmail conversations."""

    STR_FIELD = 'id'

    @staticmethod
    def _convert_conversation_objects(data, reddit):
        """Convert messages and mod actions to PRAW objects."""
        result = {'messages': [], 'modActions': []}
        for thing in data['conversation']['objIds']:
            key = thing['key']
            thing_data = data[key][thing['id']]
            result[key].append(reddit._objector.objectify(thing_data))
        return result

    @staticmethod
    def _convert_user_summary(data, reddit):
        """Convert dictionaries of recent user history to PRAW objects."""
        parsers = {'recentComments':
                   reddit._objector.parsers[reddit.config.kinds['comment']],
                   'recentConvos': ModmailConversation,
                   'recentPosts':
                   reddit._objector.parsers[reddit.config.kinds['submission']]}
        for kind, parser in parsers.items():
            objects = []
            for thing_id, summary in data[kind].items():
                thing = parser(reddit, id=thing_id.rsplit('_', 1)[-1])
                if parser is not ModmailConversation:
                    del summary['permalink']
                for key, value in summary.items():
                    setattr(thing, key, value)
                objects.append(thing)
            # Sort by id, oldest to newest
            data[kind] = sorted(
                objects,
                key=lambda x: int(x.id, base=36), reverse=True)

    @classmethod
    def parse(cls, data, reddit,  # pylint: disable=arguments-differ
              convert_objects=True):
        """Return an instance of ModmailConversation from ``data``.

        :param data: The structured data.
        :param reddit: An instance of :class:`.Reddit`.
        :param convert_objects: If True, convert message and mod action data
            into objects (default: True).

        """
        conversation = data['conversation']

        conversation['authors'] = [reddit._objector.objectify(author)
                                   for author in conversation['authors']]
        for entity in 'owner', 'participant':
            conversation[entity] = reddit._objector.objectify(
                conversation[entity])

        if data.get('user'):
            cls._convert_user_summary(data['user'], reddit)
            conversation['user'] = reddit._objector.objectify(data['user'])
        if convert_objects:
            conversation.update(cls._convert_conversation_objects(data,
                                                                  reddit))

        conversation = reddit._objector._snake_case_keys(conversation)

        return cls(reddit, _data=conversation)

    def __init__(self, reddit, id=None,  # pylint: disable=redefined-builtin
                 mark_read=False, _data=None):
        """Construct an instance of the ModmailConversation object.

        :param mark_read: If True, conversation is marked as read
            (default: False).

        """
        super(ModmailConversation, self).__init__(reddit, _data)
        if bool(id) == bool(_data):
            raise TypeError('Either `id` or `_data` must be provided.')

        if id:
            self.id = id  # pylint: disable=invalid-name
        if mark_read:
            self._info_params = {'markRead': True}

    def _build_conversation_list(self, other_conversations):
        """Return a comma-separated list of conversation IDs."""
        conversations = [self] + (other_conversations or [])
        return ','.join(conversation.id for conversation in conversations)

    def _info_path(self):
        return API_PATH['modmail_conversation'].format(id=self.id)

    def archive(self):
        """Archive the conversation.

        Example:

        .. code:: python

           reddit.subreddit('redditdev').modmail('2gmz').archive()

        """
        self._reddit.post(API_PATH['modmail_archive'].format(id=self.id))

    def highlight(self):
        """Highlight the conversation.

        Example:

        .. code:: python

           reddit.subreddit('redditdev').modmail('2gmz').highlight()

        """
        self._reddit.post(API_PATH['modmail_highlight'].format(id=self.id))

    def mute(self):
        """Mute the non-mod user associated with the conversation.

        Example:

        .. code:: python

           reddit.subreddit('redditdev').modmail('2gmz').mute()

        """
        self._reddit.request('POST',
                             API_PATH['modmail_mute'].format(id=self.id))

    def read(self, other_conversations=None):  # noqa: D207, D301
        """Mark the conversation(s) as read.

        :param other_conversations: A list of other conversations to mark
            (default: None).

        For example, to mark the conversation as read along with other recent
        conversations from the same user:

        .. code:: python

           subreddit = reddit.subreddit('redditdev')
           conversation = subreddit.modmail.conversation('2gmz')
           conversation.read(\
other_conversations=conversation.user.recent_convos)

        """
        data = {'conversationIds': self._build_conversation_list(
            other_conversations)}
        self._reddit.post(API_PATH['modmail_read'], data=data)

    def reply(self, body, author_hidden=False, internal=False):
        """Reply to the conversation.

        :param body: The markdown formatted content for a message.
        :param author_hidden: When True, author is hidden from non-moderators
            (default: False).
        :param internal: When True, message is a private moderator note,
            hidden from non-moderators (default: False).
        :returns: A :class:`~.ModmailMessage` object for the newly created
            message.

        For example, to reply to the non-mod user while hiding your username:

        .. code:: python

           conversation = reddit.subreddit('redditdev').modmail('2gmz')
           conversation.reply('Message body', author_hidden=True)

        To create a private moderator note on the conversation:

        .. code:: python

           conversation.reply('Message body', internal=True)

        """
        data = {'body': body, 'isAuthorHidden': author_hidden,
                'isInternal': internal}
        response = self._reddit.post(API_PATH['modmail_conversation']
                                     .format(id=self.id), data=data)
        message_id = response['conversation']['objIds'][-1]['id']
        message_data = response['messages'][message_id]
        return self._reddit._objector.objectify(message_data)

    def unarchive(self):
        """Unarchive the conversation.

        Example:

        .. code:: python

           reddit.subreddit('redditdev').modmail('2gmz').unarchive()

        """
        self._reddit.post(API_PATH['modmail_unarchive'].format(id=self.id))

    def unhighlight(self):
        """Un-highlight the conversation.

        Example:

        .. code:: python

           reddit.subreddit('redditdev').modmail('2gmz').unhighlight()

        """
        self._reddit.request('DELETE',
                             API_PATH['modmail_highlight'].format(id=self.id))

    def unmute(self):
        """Unmute the non-mod user associated with the conversation.

        Example:

        .. code:: python

           reddit.subreddit('redditdev').modmail('2gmz').unmute()

        """
        self._reddit.request('POST',
                             API_PATH['modmail_unmute'].format(id=self.id))

    def unread(self, other_conversations=None):  # noqa: D207, D301
        """Mark the conversation(s) as unread.

        :param other_conversations: A list of other conversations to mark
            (default: None).

        For example, to mark the conversation as unread along with other recent
        conversations from the same user:

        .. code:: python

           subreddit = reddit.subreddit('redditdev')
           conversation = subreddit.modmail.conversation('2gmz')
           conversation.unread(\
other_conversations=conversation.user.recent_convos)

        """
        data = {'conversationIds': self._build_conversation_list(
            other_conversations)}
        self._reddit.post(API_PATH['modmail_unread'], data=data)


class ModmailObject(RedditBase):
    """A base class for objects within a modmail conversation."""

    AUTHOR_ATTRIBUTE = 'author'
    STR_FIELD = 'id'

    def __setattr__(self, attribute, value):
        """Objectify the AUTHOR_ATTRIBUTE attribute."""
        if attribute == self.AUTHOR_ATTRIBUTE:
            value = self._reddit._objector.objectify(value)
        super(ModmailObject, self).__setattr__(attribute, value)


class ModmailAction(ModmailObject):
    """A class for moderator actions on modmail conversations."""


class ModmailMessage(ModmailObject):
    """A class for modmail messages."""
