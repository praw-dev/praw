from ...const import API_PATH as API_PATH
from .mixins import BaseListingMixin as BaseListingMixin, RisingListingMixin as RisingListingMixin
from typing import Any

class DomainListing(BaseListingMixin, RisingListingMixin):
    def __init__(self, reddit: Any, domain: Any) -> None: ...
