"""Represent the Trophy class."""
from .base import PRAWBase


class Trophy(PRAWBase):
    """Represent a trophy.

    End users should not instantiate this class directly.
    :meth:`.Redditor.trophies` can be used to get a list
    of the redditor's trophies.

    """

    def __init__(self, reddit, _data):
        """Initialize a Trophy instance.

        :param reddit: An instance of :class:`.Reddit`.
        :param _data: The structured data, assumed to be a dict
            and key ``'name'`` must be provided.

        """
        assert isinstance(_data, dict) and 'name' in _data
        super(Trophy, self).__init__(reddit, _data)

    def __str__(self):
        """Return a name of the trophy."""
        return self.name  # pylint: disable=no-member
