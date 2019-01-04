"""Provide classes related to widgets."""

from json import dumps

from ...const import API_PATH
from ..base import PRAWBase
from ..list.base import BaseList


class Button(PRAWBase):
    """Class to represent a single button inside a :class:`.ButtonWidget`."""


class Image(PRAWBase):
    """Class to represent an image that's part of a :class:`.ImageWidget`."""


class ImageData(PRAWBase):
    """Class for image data that's part of a :class:`.CustomWidget`."""


class MenuLink(PRAWBase):
    """Class to represent a single link inside a menu or submenu."""


class Submenu(BaseList):
    """Class to represent a submenu of links inside a menu."""

    CHILD_ATTRIBUTE = 'children'


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

    @property
    def id_card(self):
        """Get this subreddit's :class:`.IDCard` widget."""
        if self._id_card is None:
            self._id_card = self.items[self.layout['idCardWidget']]
        return self._id_card

    @property
    def items(self):
        """Get this subreddit's widgets as a dict from ID to widget."""
        if self._items is None:
            self._items = {}
            for item_name, data in self._raw_items.items():
                data['subreddit'] = self.subreddit
                self._items[item_name] = self._reddit._objector.objectify(data)
        return self._items

    @property
    def mod(self):
        """Get an instance of :class:`.SubredditWidgetsModeration`."""
        if self._mod is None:
            self._mod = SubredditWidgetsModeration(self.subreddit,
                                                   self._reddit)
        return self._mod

    @property
    def moderators_widget(self):
        """Get this subreddit's :class:`.ModeratorsWidget`."""
        if self._moderators_widget is None:
            self._moderators_widget = self.items[
                self.layout['moderatorWidget']]
        return self._moderators_widget

    @property
    def sidebar(self):
        """Get a list of Widgets that make up the sidebar."""
        if self._sidebar is None:
            self._sidebar = [self.items[widget_name] for widget_name in
                             self.layout['sidebar']['order']]
        return self._sidebar

    @property
    def topbar(self):
        """Get a list of Widgets that make up the top bar."""
        if self._topbar is None:
            self._topbar = [self.items[widget_name]
                            for widget_name in self.layout['topbar']['order']]
        return self._topbar

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
        if not attr.startswith('_') and not self._fetched:
            self._fetch()
            return getattr(self, attr)
        raise AttributeError('{!r} object has no attribute {!r}'
                             .format(self.__class__.__name__, attr))

    def __init__(self, subreddit):
        """Initialize the class.

        :param subreddit: The :class:`.Subreddit` the widgets belong to.

        """
        # set private variables used with properties to None.
        self._id_card = self._moderators_widget = self._sidebar = None
        self._topbar = self._items = self._raw_items = self._mod = None

        self._fetched = False
        self.subreddit = subreddit
        self.progressive_images = False

        super(SubredditWidgets, self).__init__(subreddit._reddit, {})

    def __repr__(self):
        """Return an object initialization representation of the object."""
        return 'SubredditWidgets(subreddit={subreddit!r})'.format(
            subreddit=self.subreddit)

    def _fetch(self):
        data = self._reddit.get(
            API_PATH['widgets'].format(subreddit=self.subreddit),
            params={'progressive_images': self.progressive_images})

        self._raw_items = data.pop('items')
        super(SubredditWidgets, self).__init__(self.subreddit._reddit, data)

        # reset private variables used with properties to None.
        self._id_card = self._moderators_widget = self._sidebar = None
        self._topbar = self._items = None

        self._fetched = True


class SubredditWidgetsModeration(object):
    """Class for moderating a subreddit's widgets."""

    def __init__(self, subreddit, reddit):
        """Initialize the class."""
        self._subreddit = subreddit
        self._reddit = reddit

    def _create_widget(self, payload):
        path = API_PATH['widget_create'].format(subreddit=self._subreddit)
        widget = self._reddit.post(path, data={'json': dumps(payload)})
        widget.subreddit = self._subreddit
        return widget

    def add_text_area(self, short_name, text, styles, **other_settings):
        """Add and return a text area widget."""
        text_area = {'shortName': short_name, 'text': text, 'styles': styles,
                     'kind': 'textarea'}
        text_area.update(other_settings)
        return self._create_widget(text_area)


class Widget(PRAWBase):
    """Base class to represent a Widget."""

    @property
    def mod(self):
        """Get an instance of :class:`.WidgetModeration` for this widget."""
        if self._mod is None:
            self._mod = WidgetModeration(self, self.subreddit, self._reddit)
        return self._mod

    def __eq__(self, other):
        """Check equality against another object."""
        if isinstance(other, Widget):
            return self.id.lower() == other.id.lower()
        return str(other).lower() == self.id.lower()

    # pylint: disable=invalid-name
    def __init__(self, reddit, _data):
        """Initialize an instance of the class."""
        self.subreddit = ''  # in case it isn't in _data
        self.id = ''  # in case it isn't in _data
        super(Widget, self).__init__(reddit, _data)
        self._mod = None


class ButtonWidget(Widget, BaseList):
    """Class to represent a widget containing one or more buttons.

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

    """

    CHILD_ATTRIBUTE = 'buttons'


class Calendar(Widget):
    """Class to represent a calendar widget.

    Find an existing one:

    .. code-block:: python

       calendar = None
       widgets = reddit.subreddit('redditdev').widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.Calendar):
               calendar = widget
               break

       print(calendar.googleCalendarId)

    """


class CommunityList(Widget, BaseList):
    """Class to represent a Related Communities widget.

    Find an existing one:

    .. code-block:: python

       related = None
       widgets = reddit.subreddit('redditdev').widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.CommunityList):
               related = widget
               break

       print(related)
    """

    CHILD_ATTRIBUTE = 'data'


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

    """

    def __init__(self, reddit, _data):
        """Initialize the class."""
        _data['imageData'] = [ImageData(reddit, data)
                              for data in _data.pop('imageData')]
        super(CustomWidget, self).__init__(reddit, _data)


class IDCard(Widget):
    """Class to represent an ID card widget.

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       id_card = widgets.id_card
       print(id_card.subscribersText)

    """


class ImageWidget(Widget, BaseList):
    """Class to represent an image widget.

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

    """

    CHILD_ATTRIBUTE = 'data'


class Menu(Widget, BaseList):
    """Class to represent the top menu widget of a subreddit.

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
                       print(child.text, child.url)
               else:  # MenuLink
                   print(item.text, item.url)

    """

    CHILD_ATTRIBUTE = 'data'


class ModeratorsWidget(Widget, BaseList):
    """Class to represent a moderators widget.

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       print(widgets.moderators_widget)

    """

    CHILD_ATTRIBUTE = 'mods'


class PostFlairWidget(Widget, BaseList):
    """Class to represent a post flair widget.

    Find an existing one:

    .. code-block:: python

       post_flair_widget = None
       widgets = reddit.subreddit('redditdev').widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.PostFlairWidget):
               post_flair_widget = widget
               break

       for flair in post_flair_widget:
           print(flair['text'])

    """

    def __init__(self, reddit, _data):
        """Initialize a PostFlairWidget."""
        order = _data['order']
        templates = _data['templates']
        for i, template in enumerate(order):
            order[i] = templates[template]
        super(PostFlairWidget, self).__init__(reddit, _data)

    CHILD_ATTRIBUTE = 'order'


class RulesWidget(Widget, BaseList):
    """Class to represent a rules widget.

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       rules_widget = None
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.RulesWidget):
               rules_widget = widget
               break
       from pprint import pprint; pprint(rules)

    """

    CHILD_ATTRIBUTE = 'data'


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
    """


class WidgetModeration(object):
    """Class for moderating a particular widget."""

    def __init__(self, widget, subreddit, reddit):
        """Initialize the widget moderation object."""
        self.widget = widget
        self._reddit = reddit
        self._subreddit = subreddit

    def delete(self):
        """Delete the widget."""
        path = API_PATH['widget_modify'].format(widget_id=self.widget.id,
                                                subreddit=self._subreddit)
        self._reddit.request('DELETE', path)

    def update(self, **kwargs):
        """Update the widget. Returns the updated widget.

        Parameters differ based on the type of widget. See
        `Reddit documentation
        <https://www.reddit.com/dev/api#PUT_api_widget_{widget_id}>`_.
        For example, update a text widget like so:

        .. code-block:: python

           text_widget.mod.update(shortName='New text area', text='Hello!')
        """
        path = API_PATH['widget_modify'].format(widget_id=self.widget.id,
                                                subreddit=self._subreddit)
        payload = {key: value for key, value in vars(self.widget).items()
                   if not key.startswith('_')}
        del payload['subreddit']  # not JSON serializable
        payload.update(kwargs)
        widget = self._reddit.put(path, data={'json': dumps(payload)})
        widget.subreddit = self._subreddit
        return widget
