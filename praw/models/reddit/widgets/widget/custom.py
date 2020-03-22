"""Provide the CustomWidget class."""
from ..image_data import ImageData
from .widget import Widget


class CustomWidget(Widget):
    """Class to represent a custom widget.

    Find an existing one:

    .. code-block:: python

       custom = None
       widgets = reddit.subreddit('redditdev').widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.CustomWidget):
               custom = widget
               break

       print(custom.text)
       print(custom.css)

    Create one (requires proper moderator permissions):

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
       custom = widgets.mod.add_custom_widget(
           'My custom widget', '# Hello world!', '/**/', 200, [], styles)

    For more information on creation, see :meth:`.add_custom_widget`.

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {'backgroundColor': '#FFFFFF', 'headerColor': '#FF9900'}
       custom = custom.mod.update(shortName='My fav customization',
                                  styles=new_styles)

    Delete one (requires proper moderator permissions):

    .. code-block:: python

       custom.mod.delete()

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``css``                 The CSS of the widget, as a ``str``.
    ``height``              The height of the widget, as an ``int``.
    ``id``                  The widget ID.
    ``imageData``           A ``list`` of :class:`.ImageData` that belong to
                            the widget.
    ``kind``                The widget kind (always ``'custom'``).
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``'backgroundColor'`` and
                            ``'headerColor'``.
    ``stylesheetUrl``       A link to the widget's stylesheet.
    ``subreddit``           The :class:`.Subreddit` the button widget belongs
                            to.
    ``text``                The text contents, as Markdown.
    ``textHtml``            The text contents, as HTML.
    ======================= ===================================================
    """

    def __init__(self, reddit, _data):
        """Initialize the class."""
        _data["imageData"] = [
            ImageData(reddit, data) for data in _data.pop("imageData")
        ]
        super().__init__(reddit, _data=_data)
