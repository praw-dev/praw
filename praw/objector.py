"""Provides the Objector class."""
from .exceptions import APIException


class Objector(object):
    """The objector builds :class:`.RedditBase` objects."""

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

    def objectify(self, data):
        """Create RedditBase objects from data.

        :param data: The structured data.

        """
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
            assert len(errors) == 0
        elif isinstance(data, dict) and {'date', 'id', 'name'}.issubset(
                set(data.keys())):
            parser = self.parsers[self._reddit.config.kinds['redditor']]
            return parser.parse(data, self._reddit)
        elif isinstance(data, dict) and 'user' in data:
            parser = self.parsers[self._reddit.config.kinds['redditor']]
            data['user'] = parser.parse({'name': data['user']}, self._reddit)
        return data

    def register(self, kind, cls):
        """Register a class for a given kind.

        :param kind: The kind in the parsed data to map to ``cls``.
        :param cls: A RedditBase class.

        """
        self.parsers[kind] = cls
