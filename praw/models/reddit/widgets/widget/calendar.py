"""Provide the Calendar class."""
from .widget import Widget


class Calendar(Widget):
    r"""Class to represent a calendar widget.

    Find an existing one:

    .. code-block:: python

       calendar = None
       widgets = reddit.subreddit('redditdev').widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.Calendar):
               calendar = widget
               break

       print(calendar.googleCalendarId)

    Create one (requires proper moderator permissions):

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
       config = {'numEvents': 10,
                 'showDate': True,
                 'showDescription': False,
                 'showLocation': False,
                 'showTime': True,
                 'showTitle': True}
       cal_id = 'y6nm89jy427drk8l71w75w9wjn@group.calendar.google.com'
       calendar = widgets.mod.add_calendar(
           'Upcoming Events', cal_id, True, config, styles)

    For more information on creation, see :meth:`.add_calendar`.

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {'backgroundColor': '#FFFFFF', 'headerColor': '#FF9900'}
       calendar = calendar.mod.update(shortName='My fav events',
                                      styles=new_styles)

    Delete one (requires proper moderator permissions):

    .. code-block:: python

       calendar.mod.delete()

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``configuration``       A ``dict`` describing the calendar configuration.
    ``data``                A ``list`` of ``dict``\ s that represent events.
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``'calendar'``).
    ``requiresSync``        A ``bool``.
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``'backgroundColor'`` and
                            ``'headerColor'``.
    ``subreddit``           The :class:`.Subreddit` the button widget belongs
                            to.
    ======================= ===================================================
    """
