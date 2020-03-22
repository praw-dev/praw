"""Provide the RulesWidget class."""

from ....list.base import BaseList
from .widget import Widget


class RulesWidget(Widget, BaseList):
    """Class to represent a rules widget.

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       rules_widget = None
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.RulesWidget):
               rules_widget = widget
               break
       from pprint import pprint; pprint(rules_widget.data)

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {'backgroundColor': '#FFFFFF', 'headerColor': '#FF9900'}
       rules_widget.mod.update(display='compact', shortName='The LAWS',
                               styles=new_styles)

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``data``                A list of the subreddit rules.
                            Can be iterated over by iterating over the
                            :class:`.RulesWidget` (e.g. ``for rule in
                            rules_widget``).
    ``display``             The display style of the widget, either ``'full'``
                            or ``'compact'``.
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``'subreddit-rules'``).
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``'backgroundColor'``
                            and ``'headerColor'``.
    ``subreddit``           The :class:`.Subreddit` the button widget
                            belongs to.
    ======================= ===================================================
    """

    CHILD_ATTRIBUTE = "data"

    def __init__(self, reddit, _data):
        """Initialize the rules widget."""
        if self.CHILD_ATTRIBUTE not in _data:
            # .mod.update() sometimes returns payload without 'data' field
            _data[self.CHILD_ATTRIBUTE] = []
        super().__init__(reddit, _data=_data)
