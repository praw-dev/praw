"""Provide the PRAWBase superclass."""


class PRAWBase(object):
    """Superclass for all models in PRAW."""

    @classmethod
    def parse(cls, data, reddit):
        """Return an instance of ``cls`` from ``data``.

        :param data: The structured data.
        :param reddit: An instance of :class:`.Reddit`.

        """
        return cls(reddit, _data=data)

    def __init__(self, reddit, _data):
        """Initialize a PRAWModel instance.

        :param reddit: An instance of :class:`.Reddit`.

        """
        self._reddit = reddit
        if _data:
            for attribute, value in _data.items():
                setattr(self, attribute, value)
