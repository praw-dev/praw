"""Provide the Submenu class."""

from ...list.base import BaseList


class Submenu(BaseList):
    r"""Class to represent a submenu of links inside a menu.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``children``            A list of the :class:`.MenuLink`\ s in this
                            submenu. Can be iterated over by iterating over the
                            :class:`.Submenu` (e.g. ``for menu_link in
                            submenu``).
    ``text``                The name of the submenu.
    ======================= ===================================================
    """

    CHILD_ATTRIBUTE = "children"
