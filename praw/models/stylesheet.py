"""Provide the Stylesheet class."""

from .base import PRAWBase


class Stylesheet(PRAWBase):
    """Represent a stylesheet.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``images``              A ``list`` of images used by the stylesheet.
    ``stylesheet``          The contents of the stylesheet, as CSS.
    ======================= ===================================================
    """
