"""Provide the BaseList class."""
from ..base import PRAWBase


class BaseList(PRAWBase):
    """An abstract class to coerce a list into a PRAWBase."""

    CHILD_ATTRIBUTE = None

    @staticmethod
    def _convert(reddit, item):
        raise NotImplementedError('BaseList must be extended.')

    def __init__(self, reddit, _data):
        """Initialize a BaseList instance.

        :param reddit: An instance of :class:`~.Reddit`.

        """
        super(BaseList, self).__init__(reddit, _data)

        if self.CHILD_ATTRIBUTE is None:
            raise NotImplementedError('BaseList must be extended.')

        child_list = getattr(self, self.CHILD_ATTRIBUTE)
        for index, item in enumerate(child_list):
            child_list[index] = self._convert(reddit, item)

    def __contains__(self, item):
        """Test if item exists in the list."""
        return item in getattr(self, self.CHILD_ATTRIBUTE)

    def __getitem__(self, index):
        """Return the item at position index in the list."""
        return getattr(self, self.CHILD_ATTRIBUTE)[index]

    def __iter__(self):
        """Return an iterator to the list."""
        return getattr(self, self.CHILD_ATTRIBUTE).__iter__()

    def __len__(self):
        """Return the number of items in the list."""
        return len(getattr(self, self.CHILD_ATTRIBUTE))

    def __str__(self):
        """Return a string representation of the list."""
        return str(getattr(self, self.CHILD_ATTRIBUTE))
