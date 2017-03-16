from ...const import API_PATH, urlparse
from ...exceptions import ClientException
from .base import RedditBase


class ModmailConversation(RedditBase):
    """A class for modmail conversations."""
    STR_FIELD = 'id'

    @staticmethod
    def id_from_url(url):
        """Return the ID contained within a conversation URL.
        :param url: A url to a conversation in the following format:
            * https://mod.reddit.com/mail/all/2gmz
        Raise :class:`.ClientException` if URL is not a valid conversation URL.
        """
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ClientException('Invalid URL: {}'.format(url))

        submission_id = parsed.path.rsplit('/', 1)[-1]

        if not submission_id.isalnum():
            raise ClientException('Invalid URL: {}'.format(url))
        return submission_id

    @classmethod
    def parse(cls, data, reddit):
        conversation = data['conversation']

        conversation['authors'] = [reddit._objector.objectify(author)
                                   for author in conversation['authors']]
        conversation['owner'] = reddit._objector.objectify(
            conversation['owner'])

        cls._convert_user_summary(data['user'], reddit)
        conversation['user'] = reddit._objector.objectify(data['user'])
        conversation.update(cls._convert_conversation_objects(data, reddit))

        conversation = reddit._objector.snake_case_keys(conversation)

        return cls(reddit, _data=conversation)

    @classmethod
    def _convert_conversation_objects(cls, data, reddit):
        """Convert messages and mod actions to PRAW objects."""
        result = {'messages': [], 'modActions': []}
        for object in data['conversation']['objIds']:
            key = object['key']
            object_data = data[key][object['id']]
            result[key].append(reddit._objector.objectify(object_data))
        return result

    @classmethod
    def _convert_user_summary(cls, data, reddit):
        """Convert dictionaries of recent user history to PRAW objects."""
        parsers = {'recentComments':
                   reddit._objector.parsers[reddit.config.kinds['comment']],
                   'recentConvos': ModmailConversation,
                   'recentPosts':
                   reddit._objector.parsers[reddit.config.kinds['submission']],
                   }
        for kind, parser in parsers.items():
            kind_data = data[kind]
            for k, v in kind_data.items():
                v['id'] = k.rsplit('_', 1)[-1]
                del v['permalink']
            # Sort by id, oldest to newest
            sorted_kind = sorted(
                kind_data.values(),
                key=lambda x: int(x['id'], base=36), reverse=True)
            data[kind] = [parser(reddit, _data=x) for x in sorted_kind]

    def __init__(self, reddit, id=None,  # pylint: disable=redefined-builtin
                 url=None, _data=None):
        super(ModmailConversation, self).__init__(reddit, _data)

        if id is not None:
            self.id = id  # pylint: disable=invalid-name
        elif url is not None:
            self.id = self.id_from_url(url)

    def _fetch(self):
        other = self._reddit.get(API_PATH['modmail_conversation']
                                 .format(id=self.id))
        self.__dict__.update(other.__dict__)
        self._fetched = True


class ModmailObject(RedditBase):
    AUTHOR_ATTRIBUTE = 'author'
    STR_FIELD = 'id'

    def __setattr__(self, attribute, value):
        if attribute == self.AUTHOR_ATTRIBUTE:
            value = self._reddit._objector.objectify(value)
        super(RedditBase, self).__setattr__(attribute, value)


class ModmailAction(ModmailObject):
    pass


class ModmailMessage(ModmailObject):
    pass
