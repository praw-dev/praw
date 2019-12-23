from .mixins import BaseListingMixin as BaseListingMixin, RisingListingMixin as RisingListingMixin
from typing import Any
from typing import Any

from .mixins import BaseListingMixin as BaseListingMixin, RisingListingMixin as RisingListingMixin


class DomainListing(BaseListingMixin, RisingListingMixin):
    _path: Any = ...
    def __init__(self, reddit: Any, domain: Any) -> None: ...
