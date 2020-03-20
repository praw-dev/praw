"""Provide the Stylesheet class."""
from typing import TypeVar

from .base import PRAWBase

_Stylesheet = TypeVar("_Stylesheet")


class Stylesheet(PRAWBase):
    """Represent a stylesheet.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily comprehensive.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``images``              A ``list`` of images used by the stylesheet.
    ``stylesheet``          The contents of the stylesheet, as CSS.
    ======================= ===================================================
    """

    def __eq__(self, other: _Stylesheet) -> bool:
        """Check if two stylesheets are equal."""
        if isinstance(other, self.__class__):
            return (
                self.images == other.images
                and self.stylesheet == other.stylesheet
            )
        return super().__eq__(other)

    def __repr__(self):
        """Return the object's REPR."""
        return "<{} with {} characters and {} images>".format(
            self.__class__.__name__, len(self.stylesheet), len(self.images)
        )
