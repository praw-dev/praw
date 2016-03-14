"""Provides the Objector class."""


class Objector(object):
    """The objector builds RedditModel objects."""

    def __init__(self, reddit):
        """Initialize an Objector instance.

        :param reddit: An instance of :class:`~.Reddit`.

        """
        self.parsers = {}
        self.reddit = reddit

    def objectify(self, data):
        """Create RedditModel objects from data.

        :param data: The structured data.

        """
        if isinstance(data, list):
            return [self.objectify(item) for item in data]
        if 'kind' in data:
            parser = self.parsers[data['kind']]
            return parser.parse(data['data'], self.reddit)
        return data

    def register(self, key, klass):
        """Register a class for a given key.

        :param key: The key in the parsed data to map to ``klass``.
        :param klass: A RedditModel class.

        """
        self.parsers[key] = klass
