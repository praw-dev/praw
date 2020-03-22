"""Provide the Button class."""

from ...base import PRAWBase


class Button(PRAWBase):
    """Class to represent a single button inside a :class:`.ButtonWidget`.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``color``               The hex color used to outline the button.
    ``height``              Image height. Only present on image buttons.
    ``hoverState``          A ``dict`` describing the state of the button when
                            hovered over. Optional.
    ``kind``                Either ``'text'`` or ``'image'``.
    ``linkUrl``             A link that can be visited by clicking the button.
                            Only present on image buttons.
    ``text``                The text displayed on the button.
    ``url``                 If the button is a text button, a link that can be
                            visited by clicking the button.

                            If the button is an image button, the URL of a
                            Reddit-hosted image.
    ``width``               Image width. Only present on image buttons.
    ======================= ===================================================
    """
