"""Provide the RisingListingMixin class."""
from typing import Dict, Generator, TypeVar, Union
from urllib.parse import urljoin

from ...base import PRAWBase
from ..generator import ListingGenerator

Submission = TypeVar("Submission")


class RisingListingMixin(PRAWBase):
    """Mixes in the rising methods."""

    def random_rising(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Generator[Submission, None, None]:
        """Return a :class:`.ListingGenerator` for random rising submissions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(
            self._reddit,
            urljoin(self._path, "randomrising"),
            **generator_kwargs
        )

    def rising(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Generator[Submission, None, None]:
        """Return a :class:`.ListingGenerator` for rising submissions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(
            self._reddit, urljoin(self._path, "rising"), **generator_kwargs
        )
