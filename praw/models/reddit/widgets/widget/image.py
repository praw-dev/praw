"""Provide the ImageWidget class."""

from ....list.base import BaseList
from .widget import Widget


class ImageWidget(Widget, BaseList):
    r"""Class to represent an image widget.

    Find an existing one:

    .. code-block:: python

       image_widget = None
       widgets = reddit.subreddit('redditdev').widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.ImageWidget):
               image_widget = widget
               break

       for image in image_widget:
           print(image.url)

    Create one (requires proper moderator permissions):

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       image_paths = ['/path/to/image1.jpg', '/path/to/image2.png']
       image_dicts = [{'width': 600, 'height': 450, 'linkUrl': '',
                       'url': widgets.mod.upload_image(img_path)}
                      for img_path in image_paths]
       styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
       image_widget = widgets.mod.add_image_widget('My cool pictures',
                                                   image_dicts, styles)

    For more information on creation, see :meth:`.add_image_widget`.

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {'backgroundColor': '#FFFFFF', 'headerColor': '#FF9900'}
       image_widget = image_widget.mod.update(shortName='My fav images',
                                              styles=new_styles)

    Delete one (requires proper moderator permissions):

    .. code-block:: python

       image_widget.mod.delete()

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``data``                A list of the :class:`.Image`\ s in this widget.
                            Can be iterated over by iterating over the
                            :class:`.ImageWidget` (e.g. ``for img in
                            image_widget``).
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``'image'``).
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``'backgroundColor'`` and
                            ``'headerColor'``.
    ``subreddit``           The :class:`.Subreddit` the button widget belongs
                            to.
    ======================= ===================================================
    """

    CHILD_ATTRIBUTE = "data"
