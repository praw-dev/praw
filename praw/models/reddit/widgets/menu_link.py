"""Provide the MenuLink class."""

from ...base import PRAWBase


class MenuLink(PRAWBase):
    """Class to represent a single link inside a menu or submenu.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``text``                The text of the menu link.
    ``url``                 The URL that the menu item links to.
    ======================= ===================================================
    """
