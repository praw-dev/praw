"""Provide the SubredditWidgets class."""


from ....const import API_PATH
from ....util.cache import cachedproperty
from ...base import PRAWBase
from .subreddit_widgets_moderation import SubredditWidgetsModeration


class SubredditWidgets(PRAWBase):
    """Class to represent a subreddit's widgets.

    Create an instance like so:

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets

    Data will be lazy-loaded. By default, PRAW will not request progressively
    loading images from Reddit. To enable this, instantiate a SubredditWidgets
    object, then set the attribute ``progressive_images`` to ``True`` before
    performing any action that would result in a network request.

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       widgets.progressive_images = True
       for widget in widgets.sidebar:
           # do something

    Access a subreddit's widgets with the following attributes:

    .. code-block:: python

       print(widgets.id_card)
       print(widgets.moderators_widget)
       print(widgets.sidebar)
       print(widgets.topbar)

    The attribute :attr:`.id_card` contains the subreddit's ID card,
    which displays information like the number of subscribers.

    The attribute :attr:`.moderators_widget` contains the subreddit's
    moderators widget, which lists the moderators of the subreddit.

    The attribute :attr:`.sidebar` contains a list of widgets which make up
    the sidebar of the subreddit.

    The attribute :attr:`.topbar` contains a list of widgets which make up
    the top bar of the subreddit.

    To edit a subreddit's widgets, use :attr:`~.SubredditWidgets.mod`. For
    example:

    .. code-block:: python

       widgets.mod.add_text_area('My title', '**bold text**',
                                 {'backgroundColor': '#FFFF66',
                                  'headerColor': '#3333EE'})

    For more information, see :class:`.SubredditWidgetsModeration`.

    To edit a particular widget, use ``.mod`` on the widget. For example:

    .. code-block:: python

       for widget in widgets.sidebar:
           widget.mod.update(shortName='Exciting new name')

    For more information, see :class:`.WidgetModeration`.

    **Currently available Widgets**:

    - :class:`.ButtonWidget`
    - :class:`.Calendar`
    - :class:`.CommunityList`
    - :class:`.CustomWidget`
    - :class:`.IDCard`
    - :class:`.ImageWidget`
    - :class:`.Menu`
    - :class:`.ModeratorsWidget`
    - :class:`.PostFlairWidget`
    - :class:`.RulesWidget`
    - :class:`.TextArea`

    """

    @cachedproperty
    def id_card(self):
        """Get this subreddit's :class:`.IDCard` widget."""
        return self.items[self.layout["idCardWidget"]]

    @cachedproperty
    def items(self):
        """Get this subreddit's widgets as a dict from ID to widget."""
        items = {}
        for item_name, data in self._raw_items.items():
            data["subreddit"] = self.subreddit
            items[item_name] = self._reddit._objector.objectify(data)
        return items

    @cachedproperty
    def mod(self):
        """Get an instance of :class:`.SubredditWidgetsModeration`.

        .. note::

           Using any of the methods of :class:`.SubredditWidgetsModeration`
           will likely result in the data of this :class:`.SubredditWidgets`
           being outdated. To re-sync, call :meth:`.refresh`.
        """
        return SubredditWidgetsModeration(self.subreddit, self._reddit)

    @cachedproperty
    def moderators_widget(self):
        """Get this subreddit's :class:`.ModeratorsWidget`."""
        return self.items[self.layout["moderatorWidget"]]

    @cachedproperty
    def sidebar(self):
        """Get a list of Widgets that make up the sidebar."""
        return [
            self.items[widget_name]
            for widget_name in self.layout["sidebar"]["order"]
        ]

    @cachedproperty
    def topbar(self):
        """Get a list of Widgets that make up the top bar."""
        return [
            self.items[widget_name]
            for widget_name in self.layout["topbar"]["order"]
        ]

    def refresh(self):
        """Refresh the subreddit's widgets.

        By default, PRAW will not request progressively
        loading images from Reddit. To enable this,
        set the attribute ``progressive_images`` to ``True`` prior to
        calling ``refresh()``.

        .. code-block:: python

           widgets = reddit.subreddit('redditdev').widgets
           widgets.progressive_images = True
           widgets.refresh()

        """
        self._fetch()

    def __getattr__(self, attr):
        """Return the value of `attr`."""
        if not attr.startswith("_") and not self._fetched:
            self._fetch()
            return getattr(self, attr)
        raise AttributeError(
            "{!r} object has no attribute {!r}".format(
                self.__class__.__name__, attr
            )
        )

    def __init__(self, subreddit):
        """Initialize the class.

        :param subreddit: The :class:`.Subreddit` the widgets belong to.

        """
        self._raw_items = None
        self._fetched = False
        self.subreddit = subreddit
        self.progressive_images = False

        super().__init__(subreddit._reddit, {})

    def __repr__(self):
        """Return an object initialization representation of the object."""
        return "SubredditWidgets(subreddit={subreddit!r})".format(
            subreddit=self.subreddit
        )

    def _fetch(self):
        data = self._reddit.get(
            API_PATH["widgets"].format(subreddit=self.subreddit),
            params={"progressive_images": self.progressive_images},
        )

        self._raw_items = data.pop("items")
        super().__init__(self.subreddit._reddit, data)

        cached_property_names = [
            "id_card",
            "moderators_widget",
            "sidebar",
            "topbar",
            "items",
        ]
        inst_dict_pop = self.__dict__.pop
        for name in cached_property_names:
            inst_dict_pop(name, None)

        self._fetched = True
