"""Represent the Trophy class."""
from typing import TYPE_CHECKING, Any, Dict, Union

from .base import PRAWBase

if TYPE_CHECKING:  # pragma: no cover
    from .. import Reddit


class Trophy(PRAWBase):
    """Represent a trophy.

    End users should not instantiate this class directly.
    :meth:`.Redditor.trophies` can be used to get a list
    of the redditor's trophies.


    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``award_id``            The ID of the trophy (sometimes ``None``).
    ``description``         The description of the trophy (sometimes ``None``).
    ``icon_40``             The URL of a 41x41 px icon for the trophy.
    ``icon_70``             The URL of a 71x71 px icon for the trophy.
    ``name``                The name of the trophy.
    ``url``                 A relevant URL (sometimes ``None``).
    ======================= ===================================================
    """

    def __init__(self, reddit: "Reddit", _data: Dict[str, Any]):
        """Initialize a Trophy instance.

        :param reddit: An instance of :class:`.Reddit`.
        :param _data: The structured data, assumed to be a dict
            and key ``"name"`` must be provided.

        """
        assert isinstance(_data, dict) and "name" in _data
        super().__init__(reddit, _data=_data)

    def __eq__(self, other: Union["Trophy", Any]) -> bool:
        """Check if two Trophies are equal."""
        if isinstance(other, self.__class__):
            return self.name == other.name
        return super().__eq__(other)

    def __str__(self) -> str:
        """Return a name of the trophy."""
        return self.name  # pylint: disable=no-member

    def __repr__(self) -> str:
        """Return the object's REPR status."""
        return "{}(name={!r})".format(self.__class__.__name__, self.name)
