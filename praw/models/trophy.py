"""Represent the :class:`.Trophy` class."""
from typing import TYPE_CHECKING, Any, Dict, Union

from .base import PRAWBase

if TYPE_CHECKING:  # pragma: no cover
    import praw


class Trophy(PRAWBase):
    """Represent a trophy.

    End users should not instantiate this class directly. :meth:`.Redditor.trophies` can
    be used to get a list of the redditor's trophies.

    .. include:: ../../typical_attributes.rst

    =============== ===================================================
    Attribute       Description
    =============== ===================================================
    ``award_id``    The ID of the trophy (sometimes ``None``).
    ``description`` The description of the trophy (sometimes ``None``).
    ``icon_40``     The URL of a 41x41 px icon for the trophy.
    ``icon_70``     The URL of a 71x71 px icon for the trophy.
    ``name``        The name of the trophy.
    ``url``         A relevant URL (sometimes ``None``).
    =============== ===================================================

    """

    def __eq__(self, other: Union["Trophy", Any]) -> bool:
        """Check if two Trophies are equal."""
        if isinstance(other, self.__class__):
            return self.name == other.name
        return super().__eq__(other)

    def __init__(self, reddit: "praw.Reddit", _data: Dict[str, Any]):
        """Initialize a :class:`.Trophy` instance.

        :param reddit: An instance of :class:`.Reddit`.
        :param _data: The structured data, assumed to be a dict and key ``"name"`` must
            be provided.

        """
        assert isinstance(_data, dict) and "name" in _data
        super().__init__(reddit, _data=_data)

    def __repr__(self) -> str:
        """Return an object initialization representation of the instance."""
        return f"{self.__class__.__name__}(name={self.name!r})"

    def __str__(self) -> str:
        """Return a name of the trophy."""
        return self.name  # pylint: disable=no-member
