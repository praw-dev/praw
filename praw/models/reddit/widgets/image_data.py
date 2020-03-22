"""Provide the ImageData class."""
from ...base import PRAWBase


class ImageData(PRAWBase):
    """Class for image data that's part of a :class:`.CustomWidget`.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``height``              The image height.
    ``name``                The image name.
    ``url``                 The URL of the image on Reddit's servers.
    ``width``               The image width.
    ======================= ===================================================
    """
