"""Provide the Front class."""
from .mixins import ListingMixin


class Front(ListingMixin):
    """Front is a Listing class that represents the front page."""

    def __init__(self, reddit):
        """Initialize an instance of Front."""
        super(Front, self).__init__(reddit)
        self._path = '/'
