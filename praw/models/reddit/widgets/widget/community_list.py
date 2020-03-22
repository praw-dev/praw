"""Provide the CommunityList class."""

from ....list.base import BaseList
from .widget import Widget


class CommunityList(Widget, BaseList):
    r"""Class to represent a Related Communities widget.

    Find an existing one:

    .. code-block:: python

       community_list = None
       widgets = reddit.subreddit('redditdev').widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.CommunityList):
               community_list = widget
               break

       print(community_list)

    Create one (requires proper moderator permissions):

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
       subreddits = ['learnpython', reddit.subreddit('announcements')]
       community_list = widgets.mod.add_community_list('Related subreddits',
                                                       subreddits, styles,
                                                       'description')

    For more information on creation, see :meth:`.add_community_list`.

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {'backgroundColor': '#FFFFFF', 'headerColor': '#FF9900'}
       community_list = community_list.mod.update(shortName='My fav subs',
                                                  styles=new_styles)

    Delete one (requires proper moderator permissions):

    .. code-block:: python

       community_list.mod.delete()

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``data``                A ``list`` of :class:`.Subreddit`\ s. These can
                            also be iterated over by iterating over the
                            :class:`.CommunityList` (e.g. ``for sub in
                            community_list``).
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``'community-list'``).
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``'backgroundColor'`` and
                            ``'headerColor'``.
    ``subreddit``           The :class:`.Subreddit` the button widget belongs
                            to.
    ======================= ===================================================
    """

    CHILD_ATTRIBUTE = "data"
