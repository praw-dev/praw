"""Provide the Menu class."""

from ....list.base import BaseList
from .widget import Widget


class Menu(Widget, BaseList):
    r"""Class to represent the top menu widget of a subreddit.

    Menus can generally be found as the first item in a subreddit's top bar.

    .. code-block:: python

       topbar = reddit.subreddit('redditdev').widgets.topbar
       if len(topbar) > 0:
           probably_menu = topbar[0]
           assert isinstance(probably_menu, praw.models.Menu)
           for item in probably_menu:
               if isinstance(item, praw.models.Submenu):
                   print(item.text)
                   for child in item:
                       print('\t', child.text, child.url)
               else:  # MenuLink
                   print(item.text, item.url)

    Create one (requires proper moderator permissions):

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       menu_contents = [
           {'text': 'My homepage', 'url': 'https://example.com'},
           {'text': 'Python packages',
            'children': [
                {'text': 'PRAW', 'url': 'https://praw.readthedocs.io/'},
                {'text': 'requests', 'url': 'http://python-requests.org'}
            ]},
           {'text': 'Reddit homepage', 'url': 'https://reddit.com'}
       ]
       menu = widgets.mod.add_menu(menu_contents)

    For more information on creation, see :meth:`.add_menu`.

    Update one (requires proper moderator permissions):

    .. code-block:: python

       menu_items = list(menu)
       menu_items.reverse()
       menu = menu.mod.update(data=menu_items)

    Delete one (requires proper moderator permissions):

    .. code-block:: python

       menu.mod.delete()

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``data``                A list of the :class:`.MenuLink`\ s and
                            :class:`.Submenu`\ s in this widget.
                            Can be iterated over by iterating over the
                            :class:`.Menu` (e.g. ``for item in menu``).
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``'menu'``).
    ``subreddit``           The :class:`.Subreddit` the button widget belongs
                            to.
    ======================= ===================================================

    """

    CHILD_ATTRIBUTE = "data"
