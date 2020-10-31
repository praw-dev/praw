"""Provide the Listing class."""
from typing import Any, Optional

from ..base import PRAWBase


class Listing(PRAWBase):
    """A listing is a collection of RedditBase instances."""

    CHILD_ATTRIBUTE = "children"

    def __len__(self) -> int:
        """Return the number of items in the Listing."""
        return len(getattr(self, self.CHILD_ATTRIBUTE))

    def __getitem__(self, index: int) -> Any:
        """Return the item at position index in the list."""
        return getattr(self, self.CHILD_ATTRIBUTE)[index]

    def __setattr__(self, attribute: str, value: Any):
        """Objectify the CHILD_ATTRIBUTE attribute."""
        if attribute == self.CHILD_ATTRIBUTE:
            value = self._reddit._objector.objectify(value)
        super().__setattr__(attribute, value)


class FlairListing(Listing):
    """Special Listing for handling flair lists."""

    CHILD_ATTRIBUTE = "users"

    @property
    def after(self) -> Optional[Any]:
        """Return the next attribute or None."""
        return getattr(self, "next", None)


class ModeratorListing(Listing):
    """Special Listing for handling moderator lists."""

    CHILD_ATTRIBUTE = "moderators"
