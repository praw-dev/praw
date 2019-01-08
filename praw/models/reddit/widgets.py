"""Provide classes related to widgets."""

import os.path
from json import dumps, JSONEncoder

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

    def add_button_widget(self, short_name, description, buttons,
                          styles, **other_settings):
        r"""Add and return a :class:`.ButtonWidget`.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param description: Markdown text to describe the widget.
        :param buttons: A ``list`` of ``dict``\ s describing buttons, as
            specified in `Reddit docs`_. As of this writing, the format is:

            Each button is either a text button or an image button. A text
            button looks like this:

            .. code-block:: none

               {
                 "kind": "text",
                 "text": a string no longer than 30 characters,
                 "url": a valid URL,
                 "color": a 6-digit rgb hex color, e.g. `#AABBCC`,
                 "textColor": a 6-digit rgb hex color, e.g. `#AABBCC`,
                 "fillColor": a 6-digit rgb hex color, e.g. `#AABBCC`,
                 "hoverState": {...}
               }

            An image button looks like this:

            .. code-block:: none

               {
                 "kind": "image",
                 "text": a string no longer than 30 characters,
                 "linkUrl": a valid URL,
                 "url": a valid URL of a reddit-hosted image,
                 "height": an integer,
                 "width": an integer,
                 "hoverState": {...}
               }

            Both types of buttons have the field ``hoverState``. The field does
            not have to be included (it is optional). If it is included, it can
            be one of two types: text or image. A text ``hoverState`` looks
            like this:

            .. code-block:: none

               {
                 "kind": "text",
                 "text": a string no longer than 30 characters,
                 "color": a 6-digit rgb hex color, e.g. `#AABBCC`,
                 "textColor": a 6-digit rgb hex color, e.g. `#AABBCC`,
                 "fillColor": a 6-digit rgb hex color, e.g. `#AABBCC`
               }

            An image ``hoverState`` looks like this:

            .. code-block:: none

               {
                 "kind": "image",
                 "url": a valid URL of a reddit-hosted image,
                 "height": an integer,
                 "width": an integer
               }


            .. note::

               The method :meth:`.upload_image` can be used to upload images to
               Reddit for a ``url`` field that holds a Reddit-hosted image.

            .. note::

               An image ``hoverState`` may be paired with a text widget, and a
               text ``hoverState`` may be paired with an image widget.

        :param styles: A ``dict`` with keys ``backgroundColor`` and
                       ``headerColor``, and values of hex colors. For example,
                       ``{'backgroundColor': '#FFFF66', 'headerColor':
                       '#3333EE'}``.

        .. _Reddit docs: https://www.reddit.com/dev/api#POST_api_widget

        Example usage:

        .. code-block:: python

           widget_moderation = reddit.subreddit('mysub').widgets.mod
           my_image = widget_moderation.upload_image('/path/to/pic.jpg')
           buttons = [
               {
                   'kind': 'text',
                   'text': 'View source',
                   'url': 'https://github.com/praw-dev/praw',
                   'color': '#FF0000',
                   'textColor': '#00FF00',
                   'fillColor': '#0000FF',
                   'hoverState': {
                       'kind': 'text',
                       'text': 'VIEW SOURCE',
                       'color': '#FFFFFF',
                       'textColor': '#000000',
                       'fillColor': '#0000FF'
                   }
               },
               {
                   'kind': 'image',
                   'text': 'View documentation',
                   'linkUrl': 'https://praw.readthedocs.io',
                   'url': my_image,
                   'height': 200,
                   'width': 200,
                   'hoverState': {
                       'kind': 'image',
                       'url': my_image,
                       'height': 200,
                       'width': 200
                   }
               }
           ]
           styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
           new_widget = widget_moderation.add_button_widget(
               'Things to click', 'Click some of these *cool* links!',
               buttons, styles)

        """
        button_widget = {'buttons': buttons, 'description': description,
                         'kind': 'button', 'shortName': short_name,
                         'styles': styles}
        button_widget.update(other_settings)
        return self._create_widget(button_widget)

    def add_calendar(self, short_name, google_calendar_id, requires_sync,
                     configuration, styles, **other_settings):
        """Add and return a :class:`.Calendar` widget.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param google_calendar_id: An email-style calendar ID. To share a
                                   Google Calendar, make it public,
                                   then find the "Calendar ID."
        :param requires_sync: A ``bool``.
        :param configuration: A ``dict`` as specified in `Reddit docs`_.
                              Example:

                              .. code-block:: python

                                 {'numEvents': 10,
                                  'showDate': True,
                                  'showDescription': False,
                                  'showLocation': False,
                                  'showTime': True,
                                  'showTitle': True}
        :param styles: A ``dict`` with keys ``backgroundColor`` and
                       ``headerColor``, and values of hex colors. For example,
                       ``{'backgroundColor': '#FFFF66', 'headerColor':
                       '#3333EE'}``.

        .. _Reddit docs: https://www.reddit.com/dev/api#POST_api_widget

        Example usage:

        .. code-block:: python

           widget_moderation = reddit.subreddit('mysub').widgets.mod
           styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
           config = {'numEvents': 10,
                     'showDate': True,
                     'showDescription': False,
                     'showLocation': False,
                     'showTime': True,
                     'showTitle': True}
           cal_id = 'y6nm89jy427drk8l71w75w9wjn@group.calendar.google.com'
           new_widget = widget_moderation.add_calendar('Upcoming Events',
                                                       cal_id, True,
                                                       config, styles)
        """
        calendar = {'shortName': short_name,
                    'googleCalendarId': google_calendar_id,
                    'requiresSync': requires_sync,
                    'configuration': configuration,
                    'styles': styles,
                    'kind': 'calendar'}
        calendar.update(other_settings)
        return self._create_widget(calendar)

    def add_community_list(self, short_name, data, styles, **other_settings):
        """Add and return a :class:`.CommunityList` widget.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param data: A ``list`` of subreddits. Subreddits can be represented as
                     ``str`` (e.g. the string ``'redditdev'``) or as
                     :class:`.Subreddit` (e.g.
                     ``reddit.subreddit('redditdev')``). These types may be
                     mixed within the list.
        :param styles: A ``dict`` with keys ``backgroundColor`` and
                       ``headerColor``, and values of hex colors. For example,
                       ``{'backgroundColor': '#FFFF66', 'headerColor':
                       '#3333EE'}``.

        Example usage:

        .. code-block:: python

           widget_moderation = reddit.subreddit('mysub').widgets.mod
           styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
           subreddits = ['learnpython', reddit.subreddit('redditdev')]
           new_widget = widget_moderation.add_community_list('My fav subs',
                                                             subreddits,
                                                             styles)

        """
        community_list = {'data': [str(datum) for datum in data],
                          'kind': 'community-list', 'shortName': short_name,
                          'styles': styles}
        community_list.update(other_settings)
        return self._create_widget(community_list)

    def add_custom_widget(self, short_name, text, css, height, image_data,
                          styles, **other_settings):
        r"""Add and return a :class:`.CustomWidget`.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param text: The Markdown text displayed in the widget.
        :param css: The CSS for the widget, no longer than 100000 characters.

            .. note::
                As of this writing, Reddit will not accept empty CSS. If you
                wish to create a custom widget without CSS, consider using
                ``'/**/'`` (an empty comment) as your CSS.

        :param height: The height of the widget, between 50 and 500.
        :param image_data: A ``list`` of ``dict``\ s as specified in
            `Reddit docs`_. Each ``dict`` represents an image and has the
            key ``'url'`` which maps to the URL of an image hosted on
            Reddit's servers. Images should be uploaded using
            :meth:`.upload_image`.
            Example:

            .. code-block:: python

               [{'url': 'https://some.link',  # from upload_image()
                 'width': 600, 'height': 450,
                 'name': 'logo'},
                {'url': 'https://other.link',  # from upload_image()
                 'width': 450, 'height': 600,
                 'name': 'icon'}]

        :param styles: A ``dict`` with keys ``backgroundColor`` and
            ``headerColor``, and values of hex colors. For example,
            ``{'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}``.

        .. _Reddit docs: https://www.reddit.com/dev/api#POST_api_widget

        Example usage:

        .. code-block:: python

           widget_moderation = reddit.subreddit('mysub').widgets.mod
           image_paths = ['/path/to/image1.jpg', '/path/to/image2.png']
           image_urls = [widget_moderation.upload_image(img_path)
                         for img_path in image_paths]
           image_dicts = [{'width': 600, 'height': 450, 'name': 'logo',
                           'url': image_urls[0]},
                          {'width': 450, 'height': 600, 'name': 'icon',
                           'url': image_urls[1]}]
           styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
           new_widget = widget_moderation.add_custom_widget('My widget',
                                                           '# Hello world!',
                                                           '/**/', 200,
                                                           image_dicts, styles)

        """
        custom_widget = {'css': css, 'height': height, 'imageData': image_data,
                         'kind': 'custom', 'shortName': short_name,
                         'styles': styles, 'text': text}
        custom_widget.update(other_settings)
        return self._create_widget(custom_widget)

    def add_image_widget(self, short_name, data, styles, **other_settings):
        r"""Add and return an :class:`.ImageWidget`.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param data: A ``list`` of ``dict``\ s as specified in `Reddit docs`_.
            Each ``dict`` has the key ``'url'`` which maps to the URL
            of an image hosted on Reddit's servers. Images should
            be uploaded using :meth:`.upload_image`.
            Example:

            .. code-block:: python

               [{'url': 'https://some.link',  # from upload_image()
                 'width': 600, 'height': 450,
                 'linkUrl': 'https://github.com/praw-dev/praw'},
                {'url': 'https://other.link',  # from upload_image()
                 'width': 450, 'height': 600,
                 'linkUrl': 'https://praw.readthedocs.io'}]

        :param styles: A ``dict`` with keys ``backgroundColor`` and
            ``headerColor``, and values of hex colors. For example,
            ``{'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}``.

        .. _Reddit docs: https://www.reddit.com/dev/api#POST_api_widget

        Example usage:

        .. code-block:: python

           widget_moderation = reddit.subreddit('mysub').widgets.mod
           image_paths = ['/path/to/image1.jpg', '/path/to/image2.png']
           image_dicts = [{'width': 600, 'height': 450, 'linkUrl': '',
                           'url': widget_moderation.upload_image(img_path)}
                          for img_path in image_paths]
           styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
           new_widget = widget_moderation.add_image_widget('My cool pictures',
                                                           image_dicts, styles)

        """
        image_widget = {'data': data, 'kind': 'image',
                        'shortName': short_name, 'styles': styles}
        image_widget.update(other_settings)
        return self._create_widget(image_widget)

    def add_menu(self, data, **other_settings):
        r"""Add and return a :class:`.Menu` widget.

        :param data: A ``list`` of ``dict``\ s describing menu contents, as
            specified in `Reddit docs`_. As of this writing, the format is:

            .. code-block:: none

               [
                 {
                   "text": a string no longer than 20 characters,
                   "url": a valid URL
                 },

                 OR

                 {
                   "children": [
                     {
                        "text": a string no longer than 20 characters,
                        "url": a valid URL,
                     },
                     ...
                    ],
                   "text": a string no longer than 20 characters,
                 },
                 ...
               ]

        .. _Reddit docs: https://www.reddit.com/dev/api#POST_api_widget

        Example usage:

        .. code-block:: python

           widget_moderation = reddit.subreddit('mysub').widgets.mod
           menu_contents = [
               {'text': 'My homepage', 'url': 'https://example.com'},
               {'text': 'Python packages',
                'children': [
                    {'text': 'PRAW', 'url': 'https://praw.readthedocs.io/'},
                    {'text': 'requests', 'url': 'http://python-requests.org'}
                ]},
               {'text': 'Reddit homepage', 'url': 'https://reddit.com'}
           ]
           new_widget = widget_moderation.add_menu(menu_contents)

        """
        menu = {'data': data, 'kind': 'menu'}
        menu.update(other_settings)
        return self._create_widget(menu)

    def add_post_flair_widget(self, short_name, display, order, styles,
                              **other_settings):
        """Add and return a :class:`.PostFlairWidget`.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param display: Display style. Either ``'cloud'`` or ``'list'``.
        :param order: A ``list`` of flair template IDs. You can get all flair
            template IDs in a subreddit with:

            .. code-block:: python

               flairs = [f['id'] for f in subreddit.flair.link_templates]

        :param styles: A ``dict`` with keys ``backgroundColor`` and
                       ``headerColor``, and values of hex colors. For example,
                       ``{'backgroundColor': '#FFFF66', 'headerColor':
                       '#3333EE'}``.

        Example usage:

        .. code-block:: python

           subreddit = reddit.subreddit('mysub')
           widget_moderation = subreddit.widgets.mod
           flairs = [f['id'] for f in subreddit.flair.link_templates]
           styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
           new_widget = widget_moderation.add_post_flair('Some flairs', 'list',
                                                         flairs, styles)

        """
        post_flair = {'kind': 'post-flair', 'display': display,
                      'shortName': short_name, 'order': order,
                      'styles': styles}
        post_flair.update(other_settings)
        return self._create_widget(post_flair)

    def add_text_area(self, short_name, text, styles, **other_settings):
        """Add and return a :class:`.TextArea` widget.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param text: The Markdown text displayed in the widget.
        :param styles: A ``dict`` with keys ``backgroundColor`` and
                       ``headerColor``, and values of hex colors. For example,
                       ``{'backgroundColor': '#FFFF66', 'headerColor':
                       '#3333EE'}``.

        Example usage:

        .. code-block:: python

           widget_moderation = reddit.subreddit('mysub').widgets.mod
           styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
           new_widget = widget_moderation.add_text_area('My cool title',
                                                        '*Hello* **world**!',
                                                        styles)

        """
        text_area = {'shortName': short_name, 'text': text, 'styles': styles,
                     'kind': 'textarea'}
        text_area.update(other_settings)
        return self._create_widget(text_area)

    def reorder(self, new_order, section='sidebar'):
        """Reorder the widgets.

        :param new_order: A list of widgets. Represented as a ``list`` that
            contains ``Widget`` objects or widget IDs as strings.
        :param section: The section to reorder. (default: ``'sidebar'``)

        Example usage:

        .. code-block:: python

           widgets = reddit.subreddit('mysub').widgets
           order = list(widgets.sidebar)
           order.reverse()
           widgets.mod.reorder(order)

        """
        order = [thing.id if isinstance(thing, Widget) else str(thing)
                 for thing in new_order]
        path = API_PATH['widget_order'].format(subreddit=self._subreddit,
                                               section=section)
        self._reddit.patch(path, data={'json': dumps(order),
                                       'section': section})

    def upload_image(self, file_path):
        """Upload an image to Reddit and get the URL.

        :param file_path: The path to the local file.
        :returns: The URL of the uploaded image as a ``str``.

        This method is used to upload images for widgets. For example,
        it can be used in conjunction with :meth:`.add_image_widget` or
        :meth:`.add_custom_widget`.
        """
        img_data = {'filepath': os.path.basename(file_path),
                    'mimetype': 'image/jpeg'}
        if file_path.lower().endswith('.png'):
            img_data['mimetype'] = 'image/png'

        url = API_PATH['widget_lease'].format(subreddit=self._subreddit)
        # until we learn otherwise, assume this request always succeeds
        upload_lease = self._reddit.post(url, data=img_data)['s3UploadLease']
        upload_data = {item['name']: item['value']
                       for item in upload_lease['fields']}
        upload_url = 'https:{}'.format(upload_lease['action'])

        with open(file_path, 'rb') as image:
            response = self._reddit._core._requestor._http.post(
                upload_url, data=upload_data, files={'file': image})
        response.raise_for_status()

        return upload_url + '/' + upload_data['key']


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
           print(flair)
           print(post_flair_widget.templates[flair])

    """

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


class WidgetEncoder(JSONEncoder):
    """Class to encode widget-related objects."""

    def default(self, o):  # pylint: disable=E0202
        """Serialize ``PRAWBase`` objects."""
        if isinstance(o, PRAWBase):
            return {key: val for key, val in vars(o).items()
                    if not key.startswith('_')}
        return JSONEncoder.default(self, o)


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
        widget = self._reddit.put(path, data={
            'json': dumps(payload, cls=WidgetEncoder)})
        widget.subreddit = self._subreddit
        return widget
