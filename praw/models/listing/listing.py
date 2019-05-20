"""Provide the Listing class."""
from ..base import PRAWBase


class Listing(PRAWBase):
    """A listing is a collection of RedditBase instances."""

    CHILD_ATTRIBUTE = "children"

    def __len__(self):
        """Return the number of items in the Listing."""
        return len(getattr(self, self.CHILD_ATTRIBUTE))

    def __getitem__(self, index):
        """Return the item at position index in the list."""
        return getattr(self, self.CHILD_ATTRIBUTE)[index]

    def __setattr__(self, attribute, value):
        """Objectify the CHILD_ATTRIBUTE attribute."""
        if attribute == self.CHILD_ATTRIBUTE:
            value = self._reddit._objector.objectify(value)
        super(Listing, self).__setattr__(attribute, value)


class FlairListing(Listing):
    """Special Listing for handling flair lists."""

    CHILD_ATTRIBUTE = "users"

    @property
    def after(self):
        """Return the next attribute or None."""
        return getattr(self, "next", None)
