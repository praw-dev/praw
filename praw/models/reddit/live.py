"""Provide the LiveThread class."""
from ...const import API_PATH
from .base import RedditBase


class LiveThread(RedditBase):
    """An individual LiveThread object."""

    STR_FIELD = 'id'

    def __eq__(self, other):
        """Return whether the other instance equals the current.

        Note that this comparison is case sensitive.
        """
        if isinstance(other, str):
            return other == str(self)
        return (isinstance(other, self.__class__) and
                str(self) == str(other))

    def __hash__(self):
        """Return the hash of the current instance."""
        return hash(self.__class__.__name__) ^ hash(str(self))

    def __init__(self, reddit, id=None,  # pylint: disable=redefined-builtin
                 _data=None):
        """Initialize a lazy :class:``LiveThread`` instance.

        :param reddit: An instance of :class:`.Reddit`.
        :param id: A live thread ID, e.g., ``ukaeu1ik4sw5``
        """
        if bool(id) == bool(_data):
            raise TypeError('Either `id` or `_data` must be provided.')
        super(LiveThread, self).__init__(reddit, _data)
        if id:
            self.id = id  # pylint: disable=invalid-name

    def _info_path(self):
        return API_PATH['liveabout'].format(id=self.id)
