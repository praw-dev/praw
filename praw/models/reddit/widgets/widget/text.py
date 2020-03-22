"""Provide the TextArea class."""

from .widget import Widget


class TextArea(Widget):
    """Class to represent a text area widget.

    Find a text area in a subreddit:

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       text_area = None
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.TextArea):
               text_area = widget
               break
       print(text_area.text)

    Create one (requires proper moderator permissions):

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
       text_area = widgets.mod.add_text_area('My cool title',
                                             '*Hello* **world**!',
                                             styles)

    For more information on creation, see :meth:`.add_text_area`.

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {'backgroundColor': '#FFFFFF', 'headerColor': '#FF9900'}
       text_area = text_area.mod.update(shortName='My fav text',
                                        styles=new_styles)

    Delete one (requires proper moderator permissions):

    .. code-block:: python

       text_area.mod.delete()

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
    ``kind``                The widget kind (always ``'textarea'``).
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``'backgroundColor'`` and
                            ``'headerColor'``.
    ``subreddit``           The :class:`.Subreddit` the button widget belongs
                            to.
    ``text``                The widget's text, as Markdown.
    ``textHtml``            The widget's text, as HTML.
    ======================= ===================================================
    """
