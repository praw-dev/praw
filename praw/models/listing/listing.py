"""Provide the Listing class."""
from ..base import PRAWBase


class Listing(PRAWBase):
    """A listing is a collection of RedditBase instances."""

    CHILD_ATTRIBUTE = "children"

    def __init__(self, reddit, _data):
        """Initialize a Listing instance.

        :param reddit: An instance of :class:`.Reddit`.

        """
        if self.CHILD_ATTRIBUTE in _data:
            _data[self.CHILD_ATTRIBUTE] = reddit._objector \
                    .objectify(_data[self.CHILD_ATTRIBUTE])
        super(Listing, self).__init__(reddit, _data=_data)

    def __len__(self):
        """Return the number of items in the Listing."""
        return len(self._data[self.CHILD_ATTRIBUTE])

    def __getitem__(self, index):
        """Return the item at position index in the list."""
        return self._data[self.CHILD_ATTRIBUTE][index]


class FlairListing(Listing):
    """Special Listing for handling flair lists."""

    CHILD_ATTRIBUTE = "users"

    @property
    def after(self):
        """Return the next attribute or None."""
        if hasattr(self, "next"):
            return self.next  # pylint: disable=no-member
        return None
