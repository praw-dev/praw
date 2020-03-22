"""Provide the IDCard class."""


from .widget import Widget


class IDCard(Widget):
    """Class to represent an ID card widget.

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       id_card = widgets.id_card
       print(id_card.subscribersText)

    Update one (requires proper moderator permissions):

    .. code-block:: python

       widgets.id_card.mod.update(currentlyViewingText='Bots')

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    =========================== ===============================================
    Attribute                   Description
    =========================== ===============================================
    ``currentlyViewingCount``   The number of Redditors viewing the subreddit.
    ``currentlyViewingText``    The text displayed next to the view count. For
                                example, "users online".
    ``description``             The subreddit description.
    ``id``                      The widget ID.
    ``kind``                    The widget kind (always ``'id-card'``).
    ``shortName``               The short name of the widget.
    ``styles``                  A ``dict`` with the keys ``'backgroundColor'``
                                and ``'headerColor'``.
    ``subreddit``               The :class:`.Subreddit` the button widget
                                belongs to.
    ``subscribersCount``        The number of subscribers to the subreddit.
    ``subscribersText``         The text displayed next to the subscriber
                                count. For example, "users subscribed".
    =========================== ===============================================
    """
