"""Provide the DomainListing class."""
from typing import TYPE_CHECKING

from ...const import API_PATH
from .mixins import BaseListingMixin, RisingListingMixin

if TYPE_CHECKING:  # pragma: no cover
    from ... import Reddit


class DomainListing(BaseListingMixin, RisingListingMixin):
    """Provide a set of functions to interact with domain listings."""

    def __init__(self, reddit: "Reddit", domain: str):
        """Initialize a DomainListing instance.

        :param reddit: An instance of Reddit.
        :param domain: The domain for which to obtain listings.

        """
        super().__init__(reddit, _data=None)
        self._path = API_PATH["domain"].format(domain=domain)
