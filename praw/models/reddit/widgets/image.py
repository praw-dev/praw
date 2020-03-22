"""Provide the Image class."""

from ...base import PRAWBase


class Image(PRAWBase):
    """Class to represent an image that's part of a :class:`.ImageWidget`.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``height``              Image height.
    ``linkUrl``             A link that can be visited by clicking the image.
    ``url``                 The URL of the (Reddit-hosted) image.
    ``width``               Image width.
    ======================= ===================================================
    """
