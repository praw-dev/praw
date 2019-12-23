from .mixins import BaseListingMixin as BaseListingMixin, \
    RisingListingMixin as RisingListingMixin
from ...reddit import Reddit


class DomainListing(BaseListingMixin, RisingListingMixin):
    def __init__(self, reddit: Reddit, domain: str) -> None: ...
