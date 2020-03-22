"""Provide the PostFlairWidget class."""

from ....list.base import BaseList
from .widget import Widget


class PostFlairWidget(Widget, BaseList):
    r"""Class to represent a post flair widget.

    Find an existing one:

    .. code-block:: python

       post_flair_widget = None
       widgets = reddit.subreddit('redditdev').widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.PostFlairWidget):
               post_flair_widget = widget
               break

       for flair in post_flair_widget:
           print(flair)
           print(post_flair_widget.templates[flair])

    Create one (requires proper moderator permissions):

    .. code-block:: python

       subreddit = reddit.subreddit('redditdev')
       widgets = subreddit.widgets
       flairs = [f['id'] for f in subreddit.flair.link_templates]
       styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
       post_flair = widgets.mod.add_post_flair_widget('Some flairs', 'list',
                                                      flairs, styles)

    For more information on creation, see :meth:`.add_post_flair_widget`.

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {'backgroundColor': '#FFFFFF', 'headerColor': '#FF9900'}
       post_flair = post_flair.mod.update(shortName='My fav flairs',
                                          styles=new_styles)

    Delete one (requires proper moderator permissions):

    .. code-block:: python

       post_flair.mod.delete()

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``display``             The display style of the widget, either ``'cloud'``
                            or ``'list'``.
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``'post-flair'``).
    ``order``               A list of the flair IDs in this widget.
                            Can be iterated over by iterating over the
                            :class:`.PostFlairWidget` (e.g. ``for flair_id in
                            post_flair``).
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``'backgroundColor'`` and
                            ``'headerColor'``.
    ``subreddit``           The :class:`.Subreddit` the button widget belongs
                            to.
    ``templates``           A ``dict`` that maps flair IDs to ``dict``\ s that
                            describe flairs.
    ======================= ===================================================
    """

    CHILD_ATTRIBUTE = "order"
