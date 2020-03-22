"""Provide the ButtonWidget class."""

from ....list.base import BaseList
from .widget import Widget


class ButtonWidget(Widget, BaseList):
    r"""Class to represent a widget containing one or more buttons.

    Find an existing one:

    .. code-block:: python

       button_widget = None
       widgets = reddit.subreddit('redditdev').widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.ButtonWidget):
               button_widget = widget
               break

       for button in button_widget:
           print(button.text, button.url)

    Create one (requires proper moderator permissions):

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       buttons = [
           {
               'kind': 'text',
               'text': 'View source',
               'url': 'https://github.com/praw-dev/praw',
               'color': '#FF0000',
               'textColor': '#00FF00',
               'fillColor': '#0000FF',
               'hoverState': {
                   'kind': 'text',
                   'text': 'ecruos weiV',
                   'color': '#000000',
                   'textColor': '#FFFFFF',
                   'fillColor': '#0000FF'
               }
           },
           {
               'kind': 'text',
               'text': 'View documentation',
               'url': 'https://praw.readthedocs.io',
               'color': '#FFFFFF',
               'textColor': '#FFFF00',
               'fillColor': '#0000FF'
           },
       ]
       styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
       button_widget = widgets.mod.add_button_widget(
           'Things to click', 'Click some of these *cool* links!',
           buttons, styles)

    For more information on creation, see :meth:`.add_button_widget`.

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {'backgroundColor': '#FFFFFF', 'headerColor': '#FF9900'}
       button_widget = button_widget.mod.update(shortName='My fav buttons',
                                                styles=new_styles)

    Delete one (requires proper moderator permissions):

    .. code-block:: python

       button_widget.mod.delete()

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``buttons``             A ``list`` of :class:`.Button`\ s. These can also
                            be accessed just by iterating over the
                            :class:`.ButtonWidget` (e.g. ``for button in
                            button_widget``).
    ``description``         The description, in Markdown.
    ``description_html``    The description, in HTML.
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``'button'``).
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``'backgroundColor'`` and
                            ``'headerColor'``.
    ``subreddit``           The :class:`.Subreddit` the button widget belongs
                            to.
    ======================= ===================================================
    """

    CHILD_ATTRIBUTE = "buttons"
