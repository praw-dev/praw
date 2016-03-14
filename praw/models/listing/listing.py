"""Provide the Listing class."""
from ..base import PRAWBase


class Listing(PRAWBase):
    """A listing is a collection of RedditModel instances."""

    def __len__(self):
        """Return the number of items in the Listing."""
        return len(self.children)

    def __getitem__(self, index):
        """Return the item at position index in the list."""
        return self.children[index]

    def __setattr__(self, attribute, value):
        """Objectify the `children` attribute."""
        if attribute == 'children':
            value = self._reddit._objector.objectify(value)
        super(Listing, self).__setattr__(attribute, value)
