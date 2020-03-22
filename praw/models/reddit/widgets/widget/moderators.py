"""Provide the ModeratorsWidget class."""

from ....list.base import BaseList
from .widget import Widget


class ModeratorsWidget(Widget, BaseList):
    r"""Class to represent a moderators widget.

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       print(widgets.moderators_widget)

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {'backgroundColor': '#FFFFFF', 'headerColor': '#FF9900'}
       widgets.moderators_widget.mod.update(styles=new_styles)

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``'moderators'``).
    ``mods``                A list of the :class:`.Redditor`\ s that moderate
                            the subreddit. Can be iterated over by iterating
                            over the :class:`.ModeratorsWidget` (e.g. ``for
                            mod in widgets.moderators_widget``).
    ``styles``              A ``dict`` with the keys ``'backgroundColor'``
                            and ``'headerColor'``.
    ``subreddit``           The :class:`.Subreddit` the button widget
                            belongs to.
    ``totalMods``           The total number of moderators in the subreddit.
    ======================= ===================================================
    """

    CHILD_ATTRIBUTE = "mods"

    def __init__(self, reddit, _data):
        """Initialize the moderators widget."""
        if self.CHILD_ATTRIBUTE not in _data:
            # .mod.update() sometimes returns payload without 'mods' field
            _data[self.CHILD_ATTRIBUTE] = []
        super().__init__(reddit, _data=_data)
