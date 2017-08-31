"""Provides the Objector class."""
import re

from .exceptions import APIException


class Objector(object):
    """The objector builds :class:`.RedditBase` objects."""

    @staticmethod
    def _camel_to_snake(name):
        """Return `name` converted from camelCase to snake_case.

        Code from http://stackoverflow.com/a/1176023/.

        """
        first_break_replaced = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub(
            '([a-z0-9])([A-Z])', r'\1_\2', first_break_replaced).lower()

    @classmethod
    def _snake_case_keys(cls, dictionary):
        """Return a copy of dictionary with keys converted to snake_case.

        :param dictionary: The dict to be corrected.

        """
        return {cls._camel_to_snake(k): v for k, v in dictionary.items()}

    def __init__(self, reddit):
        """Initialize an Objector instance.

        :param reddit: An instance of :class:`~.Reddit`.

        """
        self.parsers = {}
        self._reddit = reddit

    def kind(self, instance):
        """Return the kind from the instance class.

        :param instance: An instance of a subclass of RedditBase.

        """
        for key in self.parsers:
            if isinstance(instance, self.parsers[key]):
                return key

    def _objectify_dict(self, data):
        """Create RedditBase objects from dicts.

        :param data: The structured data, assumed to be a dict.
        :returns: An instance of :class:`~.RedditBase`.

        """
        if ({'conversation', 'messages', 'modActions'}.issubset(data)):
            parser = self.parsers['ModmailConversation']
        elif {'actionTypeId', 'author', 'date'}.issubset(data):
            # Modmail mod action
            data = self._snake_case_keys(data)
            parser = self.parsers['ModmailAction']
        elif {'bodyMarkdown', 'isInternal'}.issubset(data):
            # Modmail message
            data = self._snake_case_keys(data)
            parser = self.parsers['ModmailMessage']
        elif {'isAdmin', 'isDeleted'}.issubset(data):
            # Modmail author
            data = self._snake_case_keys(data)
            # Prevent clobbering base-36 id
            del data['id']
            data['is_subreddit_mod'] = data.pop('is_mod')
            parser = self.parsers[self._reddit.config.kinds['redditor']]
        elif {'banStatus', 'muteStatus', 'recentComments'}.issubset(data):
            # Modmail user
            data = self._snake_case_keys(data)
            data['created_string'] = data.pop('created')
            parser = self.parsers[self._reddit.config.kinds['redditor']]
        elif {'displayName', 'id', 'type'}.issubset(data):
            # Modmail subreddit
            data = self._snake_case_keys(data)
            parser = self.parsers[self._reddit.config.kinds[data['type']]]
        elif ({'date', 'id', 'name'}.issubset(data)
              or {'id', 'name', 'permissions'}.issubset(data)):
            parser = self.parsers[self._reddit.config.kinds['redditor']]
        else:
            if 'user' in data:
                parser = self.parsers[self._reddit.config.kinds['redditor']]
                data['user'] = parser.parse({'name': data['user']},
                                            self._reddit)
            return data
        return parser.parse(data, self._reddit)

    def objectify(self, data):
        """Create RedditBase objects from data.

        :param data: The structured data.
        :returns: An instance of :class:`~.RedditBase`, or ``None`` if
            given ``data`` is ``None``.

        """
        # pylint: disable=too-many-return-statements
        if data is None:  # 204 no content
            return
        if isinstance(data, list):
            return [self.objectify(item) for item in data]
        if 'kind' in data and data['kind'] in self.parsers:
            parser = self.parsers[data['kind']]
            return parser.parse(data['data'], self._reddit)
        elif 'json' in data and 'data' in data['json']:
            if 'things' in data['json']['data']:  # Submission.reply
                return self.objectify(data['json']['data']['things'])
            if 'url' in data['json']['data']:  # Subreddit.submit
                # The URL is the URL to the submission, so it's removed.
                del data['json']['data']['url']
                parser = self.parsers[self._reddit.config.kinds['submission']]
            else:
                parser = self.parsers['LiveUpdateEvent']
            return parser.parse(data['json']['data'], self._reddit)
        elif 'json' in data and 'errors' in data['json']:
            errors = data['json']['errors']
            if len(errors) == 1:
                raise APIException(*errors[0])
            assert not errors

        elif isinstance(data, dict):
            return self._objectify_dict(data)

        return data

    def register(self, kind, cls):
        """Register a class for a given kind.

        :param kind: The kind in the parsed data to map to ``cls``.
        :param cls: A RedditBase class.

        """
        self.parsers[kind] = cls
