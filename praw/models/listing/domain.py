"""Provide the DomainListing class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from praw.const import API_PATH
from praw.models.listing.mixins import BaseListingMixin, RisingListingMixin

if TYPE_CHECKING:
    import praw


class DomainListing(BaseListingMixin, RisingListingMixin):
    """Provide a set of functions to interact with domain listings."""

    def __init__(self, reddit: praw.Reddit, domain: str) -> None:
        """Initialize a :class:`.DomainListing` instance.

        :param reddit: An instance of :class:`.Reddit`.
        :param domain: The domain for which to obtain listings.

        """
        super().__init__(reddit, _data=None)
        self._path = API_PATH["domain"].format(domain=domain)
