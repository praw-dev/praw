"""Provide the PRAWModel superclass."""


class PRAWModel(object):
    """Superclass for all models in PRAW."""

    def __init__(self, reddit):
        """Initialize a PRAWModel instance.

        :param reddit: An instance of :class:`.Reddit`.

        """
        self._reddit = reddit
