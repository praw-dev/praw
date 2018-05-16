"""Provide classes relating to widgets."""

from copy import deepcopy
from json import dumps
import re
import os

from ..base import PRAWBase
from ...const import API_PATH


class Dictable(PRAWBase):
    """Abstract class to represent a class that can be turned to a dict."""

    def _to_dict(self):
        self_dict = {}
        for attr_name, attr_value in self.__dict__.items():
            if not attr_name.startswith('_'):
                if isinstance(attr_value, list):
                    attr_value = [item._to_dict() if isinstance(item, Dictable)
                                  else item
                                  for item in attr_value]
                self_dict[attr_name] = attr_value
        return self_dict


# pylint: disable=no-member
class Button(Dictable):
    """Class to represent a single button inside a widget.

    Create a button like so:

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       button = widgets.button('Click me!',
                               'https://praw.readthedocs.io',
                               '#00ff00')

    Buttons can be added to new or existing button widgets in subreddits you
    moderate with appropriate permissions:

    .. code-block:: python

       other_button = widgets.button('PRAW source',
                                     'https://github.com/praw-dev/praw',
                                     '#0000a0'
       my_widget = widgets.create_button_widget('PRAW info',
                                                [button, other_button])

       # swap the order for the existing widget
       my_widget.update(buttons=[other_button, button])

    """

    def __repr__(self):
        """Return an instantiation-style representation of the object."""
        return 'Button(text={text!r}, url={url!r}, color={color!r})'.format(
            text=self.text, url=self.url, color=self.color)

    def __str__(self):
        """Return a string representation of the object."""
        return self.text


class Image(Dictable):
    """Class to represent an image that's part of a :class:`.ImageWidget`.

    An Image should hold a link to an image that is hosted on Reddit's servers.
    Image uploads are handled through :meth:`.upload_image()`.

    Create an image like this:

    .. code:: python

       widgets = reddit.subreddit('redditdev').widgets
       image_link = widgets.upload_image('/path/to/image/on/disk.jpg')
       image = widgets.image(image_link, width=600, height=400)

    An Image can be added to a new or existing :class:`.ImageWidget` in a
    subreddit you moderate with appropriate permissions:

    .. code-block:: python

       image_widget = widgets.create_image_widget('Selfies', [image])

       # upload and add a new image
       image_link = widgets.upload_image('/path/to/new/image/on/disk.png')
       image = widgets.image(image_link, width=500, height=500,
                             link_url='https://www.reddit.com/r/redditdev')

       images = image_widget.images
       images.append(image)
       image_widget.update(images=images)

    """

    def __repr__(self):
        """Return an instantiation-style representation of the object."""
        if self.linkUrl:
            return ('Image(url={url!r}, width={width!r}, height={height!r}, '
                    'linkUrl={link_url!r})').format(url=self.url,
                                                    width=self.width,
                                                    height=self.height,
                                                    link_url=self.linkUrl)
        return 'Image(url={url!r}, width={width!r}, height={height!r})'.format(
            url=self.url, width=self.width, height=self.height)

    def __str__(self):
        """Return a string representation of the object."""
        return self.url


class ImageData(Dictable):
    """Class for image data that's part of a :class:`.CustomWidget`.

    An :class:`.ImageData` should contain a link to an image that is hosted on
    Reddit's servers. Image uploads are handled through
    :meth:`.upload_image()`.

    Create image data like this:

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       image_link = widgets.upload_image('/path/to/image/on/disk.jpg')
       image_data = widgets.image_data(image_link, mypic',
                                       width=300, height=200):

    Image data can be added to a new or existing :class:`.CustomWidget` in a
    subreddit you moderate with appropriate permissions.
    Assuming existing variables ``markdown`` and ``css`` that hold Markdown
    and CSS, respectively:

    .. code-block:: python

       custom = widgets.create_custom_widget('my custom widget', height=300,
                                             text=markdown, css=css,
                                             image_data=[image_data])

       # Or add it to an existing custom widget:
       custom.update(image_data=[image_data])
    """

    def __repr__(self):
        """Return an instantiation-style representation of the object."""
        return ('ImageData(url={url!r}, name={name!r}, width={width!r}, '
                'height={height!r})').format(url=self.url,
                                             name=self.name,
                                             width=self.width,
                                             height=self.height)

    def __str__(self):
        """Return a string representation of the object."""
        return self.name


# pylint: disable=no-member
class MenuLink(Dictable):
    """Class to represent a single link inside a menu or submenu.

    Create a menu link like so:

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       menu_link = widgets.menu_link('https://praw.readthedocs.io',
                                     'PRAW Documentation')

    Menu links can be added to a new or existing :class:`.Menu` or
    :class:`.Submenu` in a subreddit you moderate with appropriate permissions:

    .. code-block:: python

       # add to new Menu
       another_menu_link = widgets.menu_link('https://reddit.com',
                                             'Reddit')
       links = [menu_link, another_menu_link]
       menu = widgets.create_menu(links)

       # add to new Submenu:
       submenu = widgets.submenu('Some links', links)

       # add it to an existing Menu:
       menu.update([another_menu_link, menu_link])

    """

    def __repr__(self):
        """Return an instantiation-style representation of the object."""
        return 'MenuLink(text={text!r}, url={url!r})'.format(
            text=self.text, url=self.url)

    def __str__(self):
        """Return a string representation of the object."""
        return self.text


# pylint: disable=no-member
class Submenu(Dictable):
    """Class to represent a submenu of links inside a menu.

    A submenu is a group of up to 10 links grouped in a dropdown menu.

    Create a submenu like so:

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       links = []
       links.append(widgets.menu_link('https://praw.readthedocs.io',
                                      'PRAW Documentation'))
       links.append(widgets.menu_link('https://reddit.com', 'Reddit'))
       submenu = widgets.submenu('My favorite sites', links)

    A Submenu can be added to a new or existing :class:`.Menu`.

    .. code-block:: python

       # add to new Menu
       menu = widgets.create_menu([submenu])

       # add it to an existing Menu:
       menu_contents = menu.children
       menu_contents.append(submenu)
       menu.update(menu_contents)

    """

    def __getitem__(self, item):
        """Get the :class:`.MenuLink` at the specified index."""
        return self.children[item]

    def __init__(self, reddit, _data):
        """Initialize the object."""
        _data = deepcopy(_data)
        self.children = [child if isinstance(child, MenuLink)
                         else MenuLink(reddit, child)
                         for child in _data.pop('children')]
        super(Submenu, self).__init__(reddit, _data)

    def __len__(self):
        """Get the number of children of this submenu."""
        return len(self.children)

    def __repr__(self):
        """Return an instantiation-style representation of the object."""
        return 'Submenu(text={text!r})'.format(
            text=self.text)

    def __str__(self):
        """Return a string representation of the object."""
        return self.text


class SubredditWidgets(PRAWBase):
    """Class to represent a subreddit's widgets.

    This class should be instantiated like so:

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets

    Calling :attr:`.Subreddit.widgets()` as a function will populate the object
    with data requested from Reddit:

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets()

    If :attr:`.Subreddit.widgets` is not called as a function, data will be
    lazy-loaded like it is for other PRAW models.

    Access a subreddit's widgets with the following attributes:

    .. code-block:: python

       print(widgets.id_card)
       print(widgets.moderators_widget)
       print(widgets.sidebar)
       print(widgets.topbar)
    """

    @property
    def id_card(self):
        """Get this subreddit's :class:`.IDCard` widget."""
        if self._id_card is None:
            self._id_card = self.items[self.layout['idCardWidget']]
        return self._id_card

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

    def __call__(self, progressive_images=False):
        """Get the subreddit's widgets.

        :param progressive_images: When True, some image links will load
            progressively.

        Calling :attr:`.Subreddit.widgets()` as a function will populate the
        object with data requested from Reddit:

        .. code-block:: python

           widgets = reddit.subreddit('redditdev').widgets()

        If :attr:`.Subreddit.widgets` is not called as a function, data will
        be lazy-loaded like it is for other PRAW models. Alternatively,
        calling a SubredditWidgets object as a function will force-refresh
        the data from Reddit:

        .. code:: python

           widgets()

        """
        data = self._reddit.get(
            API_PATH['widgets'].format(subreddit=self.subreddit),
            params={'progressive_images': progressive_images})
        self._populate(data)
        return self

    def __getattr__(self, attr):
        """Return the value of `attr`."""
        if not attr.startswith('_') and not self._fetched:
            self._fetch()
            return getattr(self, attr)
        raise AttributeError('{!r} object has no attribute {!r}'
                             .format(self.__class__.__name__, attr))

    def __init__(self, subreddit, _data=None):
        """Initialize the class.

        :param subreddit: The :class:`.Subreddit` the widgets belong to.

        """
        if _data is None:
            _data = dict()

        self._id_card = self._moderators_widget = self._sidebar = None
        self._topbar = None
        self._fetched = False
        self.subreddit = subreddit

        super(SubredditWidgets, self).__init__(subreddit._reddit, _data)

    def __repr__(self):
        """Return an object initialization representation of the object."""
        return 'SubredditWidgets(subreddit={subreddit!r})'.format(
            subreddit=str(self.subreddit))

    def _create(self, info):
        """Add and return a widget to the subreddit.

        :param info: A dict representing the widget data to be saved.
        """
        path = API_PATH['widget_create'].format(subreddit=self.subreddit)
        data = self._reddit.post(path, data={'json': dumps(info)})
        return self._objectify_widget(data)

    def _fetch(self):
        self()
        self._fetched = True

    def _objectify_widget(self, data):
        subclass = {
            'button': ButtonWidget,
            'calendar': Calendar,
            'community-list': CommunityList,
            'custom': CustomWidget,
            'id-card': IDCard,
            'image': ImageWidget,
            'menu': Menu,
            'moderators': ModeratorsWidget,
            'subreddit-rules': RulesWidget,
            'textarea': TextArea
        }.get(data['kind'], Widget)

        return subclass(self.subreddit, data)

    def _populate(self, _data):
        items = _data.pop('items')
        super(SubredditWidgets, self).__init__(self.subreddit._reddit, _data)
        self.items = {item_name: self._objectify_widget(item_data)
                      for item_name, item_data in items.items()}

        self._id_card = self._moderators_widget = self._sidebar = None
        self._topbar = None

    def button(self, text, url, color):
        """Make a :class:`.Button`.

        :param text: A label for the button, no longer than 30 characters.
        :param url: A URL that the button should lead to.
        :param color: A 6-digit rgb hex color as a string, like ``'#ff44aa'``.

        .. code-block:: python

           widgets = reddit.subreddit('redditdev').widgets
           button = widgets.button('Click me!',
                                   'https://praw.readthedocs.io',
                                   '#00ff00')

        Buttons can be added to new or existing button widgets in subreddits
        you moderate with appropriate permissions:

        .. code-block:: python

           other_button = widgets.button('PRAW source',
                                         'https://github.com/praw-dev/praw',
                                         '#0000a0'
           my_widget = widgets.create_button_widget('PRAW info',
                                                    [button, other_button])

           # swap the order for the existing widget
           my_widget.update(buttons=[other_button, button])


        """
        return Button(self._reddit, {'color': color, 'text': text, 'url': url})

    def create_button_widget(self, short_name, buttons, description=''):
        """Create a :class:`.ButtonWidget` on Reddit and return it.

        :param short_name: A short name for the widget, no longer than 30
            characters.
        :param buttons: A list of :class:`.Button`.
        :param description: A description in Markdown.

        Create a new button widget in a subreddit you moderate with
        appropriate permissions:

        .. code-block:: python

           widgets = reddit.subreddit('redditdev').widgets
           button = widgets.button('Click me!',
                                   'https://praw.readthedocs.io',
                                   '#00ff00')
           other_button = widgets.button('PRAW source',
                                         'https://github.com/praw-dev/praw',
                                         '#0000a0'
           my_widget = widgets.create_button_widget('PRAW info',
                                                    [button, other_button])

        """
        return self._create({'kind': 'button',
                             'buttons': [button._to_dict()
                                         for button in buttons],
                             'description': description,
                             'shortName': short_name})

    def create_calendar(self, short_name, google_calendar_id,
                        requires_sync=True, show_date=True,
                        show_description=True,
                        show_location=True, show_time=True, show_title=True):
        """Create a :class:`.Calendar` on Reddit and return it.

        :param short_name: A short name for the widget, no longer than 30
            characters.
        :param google_calendar_id: The ID to a public Google calendar.
        :param requires_sync: A boolean (default: True).
        :param show_date: A boolean (default: True).
        :param show_description: A boolean (default: True).
        :param show_location: A boolean (default: True).
        :param show_time: A boolean (default: True).
        :param show_title: A boolean (default: True).

        Create a new calendar in a subreddit you moderate with appropriate
        permissions:

        .. code-block:: python

           widgets = reddit.subreddit('redditdev').widgets
           cal_id = ('nytimes.com_c9hche3raajglitokho7rvu664@'
                     'group.calendar.google.com')
           calendar = widgets.create_calendar('2016 election', cal_id,
                                              show_location=False)

        """
        return self._create({'kind': 'calendar',
                             'googleCalendarId': google_calendar_id,
                             'shortName': short_name,
                             'requiresSync': requires_sync,
                             'configuration': {
                                 'showDate': show_date,
                                 'showDescription': show_description,
                                 'showLocation': show_location,
                                 'showTime': show_time,
                                 'showTitle': show_title}})

    def create_community_list(self, short_name, subreddits):
        """Create a :class:`.CommunityList` on Reddit and return it.

        :param short_name: A short name for the widget, no longer than 30
            characters.
        :param subreddits: A list of :class:`.Subreddit` or names of
            subreddits.

        Create a new community list in a subreddit you moderate with
        appropriate permissions:

        .. code-block:: python

           widgets = reddit.subreddit('redditdev').widgets
           communities = ['redditdev', 'learnpython']
           community_list = widget.create_community_list('Cool spots',
                                                         communities)

           for subreddit in community_list.subreddits:
               for post in subreddit.hot(limit=3):
                   print(post.title)

        """
        subreddits = [str(subreddit) for subreddit in subreddits]
        return self._create({'kind': 'community-list',
                             'data': subreddits,
                             'shortName': short_name})

    def create_custom_widget(self, short_name, height, text='', css='',
                             image_data=None):
        """Create a :class:`.CustomWidget` on Reddit and return it.

        :param short_name: A short name for the widget, no longer than 30
            characters.
        :param height: The height of the CustomWidget, an integer between 50
            and 500.
        :param text: The text in Markdown.
        :param css: CSS for the widget, no longer than 100000 characters.
        :param image_data: A list of :class:`.ImageData`.

        Create a new custom widget in a subreddit you moderate with
        appropriate permissions:

        .. code-block:: python

           widgets = reddit.subreddit('redditdev').widgets
           custom = widgets.create_custom_widget('x', 200,
                                                 '# Welcome to the sub!')
           print(custom.text)

        """
        image_data = image_data if image_data is not None else []
        return self._create({'kind': 'custom',
                             'css': css,
                             'height': height,
                             'imageData': [data._to_dict()
                                           for data in image_data],
                             'shortName': short_name,
                             'text': text})

    def create_image_widget(self, short_name, images):
        """Create an :class:`.ImageWidget` on Reddit and return it.

        :param short_name: A short name for the widget, no longer than 30
            characters.
        :param images: A list of :class:`.Image`.

        To use this method, you will need at least one image uploaded to Reddit
        with :meth:`.upload_image()`.

        Create a new image widget in a subreddit you moderate with
        appropriate permissions:

        .. code:: python

           widgets = reddit.subreddit('redditdev').widgets
           image_link = widgets.upload_image('/path/to/image/on/disk.jpg')
           image = widgets.image(image_link, width=600, height=400)

           image_widget = widgets.create_image_widget('Selfies', [image])

           print(image_widget.images)

        """
        return self._create({'kind': 'image',
                             'data': [image._to_dict() for image in images],
                             'shortName': short_name})

    def create_menu(self, contents):
        """Create a :class:`.Menu` on Reddit and return it.

        :param contents: A list of :class:`MenuLink` and/or :class:`.Submenu`.

        .. note:: A menu cannot be created if one already exists. If this is
            the case, either call :meth:`.Menu.delete()` on the current menu to
            delete it, or use :meth:`.Menu.update()` to update the menu
            instead of deleting it.

        Create a menu in a subreddit you moderate with appropriate permissions:

        .. code-block:: python

           widgets = reddit.subreddit('redditdev').widgets
           menu_link = widgets.menu_link('https://praw.readthedocs.io',
                                         'PRAW Documentation')
           another_menu_link = widgets.menu_link('https://reddit.com',
                                                 'Reddit')
           links = [menu_link, another_menu_link]
           submenu = widgets.submenu('Some links', links)

           third_link = widgets.menu_link('https://github.com/praw-dev/praw',
                                          'PRAW Source')

           menu = widgets.create_menu([submenu, third_link])
           from pprint import pprint; pprint(menu.children)
           print(menu[0].children)

        """
        return self._create({'kind': 'menu',
                             'data': [item._to_dict() for item in contents]})

    def create_text_area(self, short_name, text=''):
        """Create a :class:`.TextArea` on Reddit and return it.

        :param short_name: A short name for the widget, no longer than 30
            characters.
        :param text: The text of the widget.

        Create a text area in a subreddit you moderate with appropriate
        permissions:

        .. code-block:: python

           widgets = reddit.subreddit('redditdev').widgets
           text_area = widgets.create_text_area('Hello world!', 'Hi there!')
           print(text_area.text)

        """
        return self._create({'kind': 'textarea',
                             'text': text,
                             'shortName': short_name})

    def image(self, url, width, height, link_url=None):
        """Make a :class:`Image` for an image widget.

        :param url: URL of an image hosted by Reddit.
        :param width: The width of the image in pixels.
        :param height: The height of the image in pixels.
        :param link_url: The URL that the picture should link to. (default:
            None)

        An Image should hold a link to an image that is hosted on Reddit's
        servers. Image uploads are handled through :meth:`.upload_image()`.

        Create an image like this:

        .. code:: python

           widgets = reddit.subreddit('redditdev').widgets
           image_link = widgets.upload_image('/path/to/image/on/disk.jpg')
           image = widgets.image(image_link, width=600, height=400)

        An Image can be added to a new or existing :class:`.ImageWidget` in
        a subreddit you moderate with appropriate permissions:

        .. code-block:: python

           image_widget = widgets.create_image_widget('Selfies', [image])

           # upload and add a new image
           image_link = widgets.upload_image('/path/to/new/image/on/disk.png')
           image = widgets.image(image_link, width=500, height=500,
                                 link_url='https://www.reddit.com/r/redditdev')

           images = image_widget.images
           images.append(image)
           image_widget.update(images=images)

        """
        return Image(self._reddit, {'url': url, 'width': width,
                                    'height': height, 'linkUrl': link_url})

    def image_data(self, url, name, width, height):
        """Make a :class:`.ImageData` for a custom widget.

        :param url: The URL of a Reddit-hosted image. This can be obtained
            through :meth:`.upload_image()` if needed.
        :param name: The name of the image, up to 20 characters, to be used
            in CSS.
        :param width: The width of the image in pixels.
        :param height: The height of the image in pixels.

        An :class:`.ImageData` should contain a link to an image that is hosted
        on Reddit's servers. Image uploads are handled through
        :meth:`.upload_image()`.

        Create image data like this:

        .. code-block:: python

           widgets = reddit.subreddit('redditdev').widgets
           image_link = widgets.upload_image('/path/to/image/on/disk.jpg')
           image_data = widgets.image_data(image_link, mypic,
                                           width=300, height=200):

        Image data can be added to a new or existing :class:`.CustomWidget`
        in a subreddit you moderate with appropriate permissions.
        Assuming existing variables ``markdown`` and ``css`` that hold Markdown
        and CSS, respectively:

        .. code-block:: python

           custom = widgets.create_custom_widget('my custom widget', height=99,
                                                 text=markdown, css=css,
                                                 image_data=[image_data])

           # Or add it to an existing custom widget:
           custom.update(image_data=[image_data])

        """
        return ImageData(self._reddit, {'url': url, 'name': name,
                                        'width': width, 'height': height})

    def menu_link(self, url, text):
        """Make a :class:`.MenuLink`.

        :param url: URL for the menu link.
        :param text: The text to display, no more than 20 characters.

        Create a menu link like so:

        .. code-block:: python

           widgets = reddit.subreddit('redditdev').widgets
           menu_link = widgets.menu_link('https://praw.readthedocs.io',
                                         'PRAW Documentation')

        Menu links can be added to a new or existing :class:`.Menu` or
        :class:`.Submenu` in a subreddit you moderate with appropriate
        permissions:

        .. code-block:: python

           # add to new Menu
           another_menu_link = widgets.menu_link('https://reddit.com',
                                                 'Reddit')
           links = [menu_link, another_menu_link]
           menu = widgets.create_menu(links)

           # add to new Submenu:
           submenu = widgets.submenu('Some links', links)

           # add it to an existing Menu:
           menu.update([another_menu_link, menu_link])

        """
        return MenuLink(self._reddit, {'url': url, 'text': text})

    def reorder(self, order, section='sidebar'):
        """Update the order of the widgets in this subreddit.

        :param order: A list of :class:`.Widget` or widget IDs.
        :param section: Which section to re-order. Currently only
            ``'sidebar'`` is supported.

        .. code-block:: python

           widgets = reddit.subreddit('redditdev').widgets
           print(widgets.sidebar)
           widgets.reorder(reversed(widgets.sidebar))
           print(widgets.sidebar)

        """
        order = [str(widget) for widget in order]
        path = API_PATH['widget_order'].format(subreddit=self.subreddit,
                                               section=section)
        self._reddit.patch(path, data={'json': dumps(order)})

    def submenu(self, text, children):
        """Make a :class:`.Submenu`.

        :param text: A description of the submenu, no more than 20 characters.
        :param children: A list of :class:`.MenuLink`.

        .. code:: python

           widgets = reddit.subreddit('redditdev').widgets
           r_all = widgets.menu_link('https://reddit.com/r/all', 'r/all')
           tifu = widgets.menu_link('https://reddit.com/r/tifu', 'r/tifu')
           submenu = reddit.submenu('Some subreddits', [r_all, tifu])
           print(submenu.children)

        """
        return Submenu(self._reddit, {'children': children, 'text': text})

    def upload_image(self, file_path):
        """Upload an image to Reddit and get the URL.

        :param file_path: The path to a local image.

        This method can be used to upload images for widgets like
        :class:`.CustomWidget` and :class:`.ImageWidget`. It supports png
        and jpg images.

        .. code:: python

           widgets = reddit.subreddit('redditdev').widgets
           image_link = widgets.upload_image('/path/to/image/on/disk.jpg')

        """
        data = {'filepath': os.path.basename(file_path),
                'mimetype': 'image/jpeg'}
        if file_path.lower().endswith('.png'):
            data['mimetype'] = 'image/png'
        url = API_PATH['widget_lease'].format(subreddit=self.subreddit)

        # until we learn otherwise, assume this request always succeeds
        upload_lease = self._reddit.post(url, data=data)
        upload_data = {item['name']: item['value']
                       for item in upload_lease['fields']}
        upload_url = 'https:{}'.format(upload_lease['action'])

        with open(file_path, 'rb') as image:
            response = self._reddit._core._requestor._http.post(
                upload_url, data=upload_data, files={'file': image})
        response.raise_for_status()
        key = re.search(r'<Key>(.+)</Key>', response.text).group(1)
        url = 'https://styles.redditmedia.com/' + key
        return url


# pylint: disable=no-member
class Widget(PRAWBase):
    """Base class to represent a Widget."""

    def _update(self, data):
        data = self._reddit.put(
            API_PATH['widget_modify'].format(subreddit=self.subreddit,
                                             widget_id=self.id),
            data={'json': dumps(data)})
        self.__init__(self.subreddit, data)

    def __eq__(self, other):
        """Check equality against another object."""
        return str(self).lower() == str(other).lower()

    def __init__(self, subreddit, _data):
        """Initialize the object."""
        self.subreddit = subreddit
        super(Widget, self).__init__(subreddit._reddit, _data)

    def __repr__(self):
        """Return an initialization-style representation of the instance."""
        return '{}(id={!r})'.format(self.__class__.__name__, str(self))

    def __str__(self):
        """Return a string representation of the instance."""
        return self.id

    def delete(self):
        """Delete the widget from the subreddit."""
        self._reddit.delete(API_PATH['widget_modify'].format(
            subreddit=self.subreddit, widget_id=self.id))


# pylint: disable=no-member
class ButtonWidget(Widget):
    """Class to represent a widget containing one or more buttons.

    Create a new one in a subreddit you moderate with appropriate permissions:

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       button = widgets.button('Click me!',
                               'https://praw.readthedocs.io',
                               '#00ff00')
       other_button = widgets.button('PRAW source',
                                     'https://github.com/praw-dev/praw',
                                     '#0000a0'
       my_widget = widgets.create_button_widget('PRAW info',
                                                [button, other_button])

    Find an existing one:

    .. code-block:: python

       button_widget = None
       widgets = reddit.subreddit('redditdev').widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.ButtonWidget):
               button_widget = widget
               break

       print(button_widget.buttons)

    """

    def __getitem__(self, item):
        """Get a button at the specified index."""
        return self.buttons[item]

    def __init__(self, subreddit, _data):
        """Initialize the class."""
        buttons = _data.pop('buttons')
        super(ButtonWidget, self).__init__(subreddit, _data)
        self.buttons = [Button(self._reddit, button)
                        for button in buttons]

    def __len__(self):
        """Get the number of buttons."""
        return len(self.buttons)

    def update(self, short_name=None, buttons=None, description=None):
        """Update the ButtonWidget.

        :param short_name: A short name for the widget, no longer than 30
            characters.
        :param buttons: A list of :class:`.Button`.
        :param description: A description in Markdown.

        Any unset parameters will retain their previous value.

        """
        data = {'kind': 'button',
                'buttons': [button._to_dict()
                            for button in (buttons or self.buttons)],
                'description': description or self.description,
                'shortName': short_name or self.shortName}
        self._update(data)


# pylint: disable=no-member
class Calendar(Widget):
    """Class to represent a calendar widget.

    Create a new one in a subreddit you moderate with appropriate
    permissions like so:

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       cal_id = ('nytimes.com_c9hche3raajglitokho7rvu664@'
                 'group.calendar.google.com')
       calendar = widgets.create_calendar('2016 election', cal_id,
                                          show_location=False)

    Or find an existing one:

    .. code-block:: python

       calendar = None
       widgets = reddit.subreddit('redditdev').widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.Calendar):
               calendar = widget
               break

       print(calendar.googleCalendarId)

    """

    def update(self, short_name=None, google_calendar_id=None,
               requires_sync=None, show_date=None, show_description=None,
               show_location=None, show_time=None, show_title=None):
        """Update the Calendar.

        :param short_name: A short name for the widget, no longer than 30
            characters.
        :param google_calendar_id: The ID to a public Google calendar.
        :param requires_sync: A boolean.
        :param show_date: A boolean.
        :param show_description: A boolean.
        :param show_location: A boolean.
        :param show_time: A boolean.
        :param show_title: A boolean.

        Any unset parameters will retain their previous value.

        """
        data = {'kind': 'calendar',
                'googleCalendarId': (google_calendar_id or
                                     self.googleCalendarId),
                'shortName': short_name or self.shortName,
                'requiresSync': (self.requiresSync if requires_sync is None
                                 else requires_sync),
                'configuration': {
                    'showDate': (self.configuration['showDate']
                                 if show_date is None else show_date),
                    'showDescription': (self.configuration['showDescription']
                                        if show_description is None
                                        else show_description),
                    'showLocation': (self.configuration['showLocation']
                                     if show_location is None
                                     else show_location),
                    'showTime': (self.configuration['showTime']
                                 if show_time is None else show_time),
                    'showTitle': (self.configuration['showTitle']
                                  if show_title is None else show_title)}}

        self._update(data)


# pylint: disable=no-member
class CommunityList(Widget):
    """Class to represent a Related Communities widget.

    Create a new one in a subreddit you moderate with appropriate
    permissions like so:

    .. code-block:: python

       subreddits = ['redditdev', reddit.subreddit('learnpython')]
       widgets = reddit.subreddit('redditdev').widgets
       community_list = widgets.create_community_list('Friends of the sub',
                                                      subreddits)
       print(community_list.subredits)

    """

    @property
    def subreddits(self):
        """Get a list of Subreddit objects from the list."""
        if self._subreddits is None:
            if isinstance(self.data[0], dict):
                self._subreddits = [self._reddit.subreddit(subreddit['name'])
                                    for subreddit in self.data]
            else:
                # Reddit returns plain strings when updating,
                # but dicts when querying
                self._subreddits = [self._reddit.subreddit(subreddit) for
                                    subreddit in self.data]
        return self._subreddits

    def __getitem__(self, item):
        """Get the :class:`.Subreddit` at index ``item``."""
        return self.subreddits[item]

    def __init__(self, subreddit, _data):
        """Initialize the object."""
        super(CommunityList, self).__init__(subreddit, _data)

        self._subreddits = None

    def __len__(self):
        """Get the number of subreddits in this list."""
        return len(self.subreddits)

    def update(self, short_name=None, subreddits=None):
        """Update the CommunityList.

        :param short_name: A short name for the widget, no longer than 30
            characters.
        :param subreddits: A list of :class:`.Subreddit` or names of
            subreddits.

        Any unset parameters will retain their previous value.

        Assuming you have an instance of :class:`.CommunityList` called
        ``community_list``:

        .. code-block:: python

           subreddits = ['redditdev', 'learnpython']
           subreddits.append(reddit.subreddit('changelog'))
           community_list.update(subreddits=subreddits)

        """
        if subreddits:
            subreddits = [str(subreddit) for subreddit in subreddits]
        data = {'kind': 'community-list',
                'data': [str(subreddit) for subreddit in
                         (subreddits or self.subreddits)],
                'shortName': short_name or self.shortName}
        self._update(data)


# pylint: disable=no-member
class CustomWidget(Widget):
    """Class to represent a custom widget.

    Create a new custom widget in a subreddit you moderate with approproate
    permissions:

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       custom = widgets.create_custom_widget('x', 200,
                                             '# Welcome to the sub!')
       print(custom.text)

    Update it with new :class:`.ImageData`:

    .. code-block:: python

       image_link = widgets.upload_image('/path/to/image/on/disk.jpg')
       image_data = widgets.image_data(image_link, mypic,
                                       width=300, height=200):

       custom.update(image_data=[image_data])
       print(len(custom.imageData))

    """

    def __init__(self, subreddit, _data):
        """Initialize the class."""
        _data['imageData'] = [ImageData(subreddit._reddit, data)
                              for data in _data.pop('imageData')]
        super(CustomWidget, self).__init__(subreddit, _data)

    def update(self, short_name=None, height=None, text=None, css=None,
               image_data=None):
        """Update the CustomWidget.

        :param short_name: A short name for the widget, no longer than 30
            characters.
        :param height: The height of the CustomWidget, an integer between 50
            and 500.
        :param text: The text in Markdown.
        :param css: CSS for the widget, no longer than 100000 characters.
        :param image_data: A list of :class:`.ImageData`.

        Any unset parameters will retain their previous value.

        """
        data = {'kind': 'custom', 'css': css or self.css,
                'height': height or self.height,
                'imageData': image_data or self.imageData,
                'shortName': short_name or self.shortName,
                'text': text or self.text}
        self._update(data)


# pylint: disable=no-member
class IDCard(Widget):
    """Class to represent an ID card widget.

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       id_card = widgets.id_card
       print(id_card.subscribersText)

    """

    def update(self, short_name=None, currently_viewing_text=None,
               subscribers_text=None):
        """Update the IDCard.

        :param short_name: A short name for the widget, no longer than 30
            characters.
        :param currently_viewing_text: Text to display next to the number of
            current subreddit viewers, no longer than 30 characters.
        :param subscribers_text: Text to display next to the number of
            subscribers, no longer than 30 characters.

        Any unset parameters will retain their previous value.

        """
        data = {'kind': 'id-card',
                'currentlyViewingText': (currently_viewing_text or
                                         self.currentlyViewingText),
                'subscribersText': subscribers_text or self.subscribersText,
                'shortName': short_name or self.shortName}
        self._update(data)


# pylint: disable=no-member
class ImageWidget(Widget):
    """Class to represent an image widget.

    Create a new image widget on Reddit in a subreddit you moderate with
    appropriate permissions:

    .. code:: python

       widgets = reddit.subreddit('redditdev').widgets
       image_link = widgets.upload_image('/path/to/image/on/disk.jpg')
       image = widgets.image(image_link, width=600, height=400)

       image_widget = widgets.create_image_widget('Selfies', [image])

       print(image_widget[0])
    """

    @property
    def images(self):
        """Get all the :class:`.Image` that make up this widget."""
        if self._images is None:
            self._images = [Image(self._reddit, image) for image in self.data]
        return self._images

    def __getitem__(self, item):
        """Get the image at the specified index."""
        return self.images[item]

    def __init__(self, subreddit, _data):
        """Initialize the object."""
        super(ImageWidget, self).__init__(subreddit, _data)

        self._images = None

    def __len__(self):
        """Get the number of images in this widget."""
        return len(self.images)

    def update(self, short_name=None, images=None):
        """Update the ImageWidget.

        :param short_name: A short name for the widget, no longer than 30
            characters.
        :param images: A list of :class:`.Image`.

        Any unset parameters will retain their previous value.

        """
        data = {'kind': 'image',
                'data': [image._to_dict()
                         for image in (images or self.images)],
                'shortName': short_name or self.shortName}
        self._update(data)


class Menu(Widget):
    """Class to represent the top menu widget of a subreddit.

    Create a new menu on Reddit in a subreddit you moderate with appropriate
    permissions:

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       menu_link = widgets.menu_link('https://praw.readthedocs.io',
                                     'PRAW Documentation')
       another_menu_link = widgets.menu_link('https://reddit.com',
                                             'Reddit')
       links = [menu_link, another_menu_link]
       submenu = widgets.submenu('Some links', links)

       third_link = widgets.menu_link('https://github.com/praw-dev/praw',
                                      'PRAW Source')

       menu = widgets.create_menu([submenu, third_link])
       from pprint import pprint; pprint(menu.children)
       print(menu[0].children)

    """

    @property
    def children(self):
        """Get the items contained within this menu."""
        if self._children is None:
            self._children = [self._parse_child(item) for item in self.data]
        return self._children

    def __getitem__(self, item):
        """Get the item at the specified index."""
        return self.children[item]

    def __init__(self, subreddit, _data):
        """Initialize this object."""
        super(Menu, self).__init__(subreddit, _data)

        self._children = None

    def __len__(self):
        """Get the number of top-level items in this menu."""
        return len(self.children)

    def _parse_child(self, data):
        if 'children' in data.keys():
            parser = Submenu
        else:
            parser = MenuLink
        return parser.parse(data, self._reddit)

    def update(self, contents):
        """Update the menu.

        :param contents: A list of :class:`MenuLink` and/or :class:`.Submenu`.

        """
        data = {'kind': 'menu',
                'data': [item._to_dict() for item in contents]}
        self._update(data)


# pylint: disable=no-member
class ModeratorsWidget(Widget):
    """Class to represent a moderators widget.

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       print(widgets.moderators_widget.moderators)

    """

    @property
    def moderators(self):
        """Get a list of Redditors from this widget."""
        if self._moderators is None:
            self._moderators = [self._reddit.redditor(moderator['name'])
                                for moderator in self.mods]
        return self._moderators

    def __getitem__(self, item):
        """Return the moderator at the specified index."""
        return self.moderators[item]

    def __init__(self, subreddit, _data):
        """Initialize the object."""
        super(ModeratorsWidget, self).__init__(subreddit, _data)

        self._moderators = None

    def __len__(self):
        """Get the number of moderators in this widget."""
        return len(self.moderators)


class RulesWidget(Widget):
    """Class to represent a rules widget.

    Update the display to be compact in a subreddit you moderate with
    appropriate permissions:

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       rules_widget = None
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.RulesWidget):
               rules_widget = widget
               break
       rules_widget.update(display='compact')
    """

    def update(self, short_name=None, display=None):
        """Update the RulesWidget.

        :param short_name: A short name for the widget, no longer than 30
            characters.
        :param display: ``'compact'`` or ``'full'``.

        Any unset parameters will retain their previous value.

        .. note:: The ``short_name`` parameter is documented in Reddit's API
            documentation but does not appear to have any effect.

        """
        self._update({'kind': 'subreddit-rules',
                      'display': display or self.display,
                      'shortName': short_name or self.shortName})


# pylint: disable=no-member
class TextArea(Widget):
    """Class to represent a text area widget.

    Create a new text area in a subreddit you moderate with appropriate
    permissions:

    .. code-block:: python

       widgets = reddit.subreddit('redditdev').widgets
       text_area = widgets.create_text_area('Hello world!', 'Hi there!')
       print(text_area.text)

    """

    def update(self, short_name=None, text=None):
        """Update the TextArea.

        :param short_name: A short name for the widget, no longer than 30
            characters.
        :param text: The text with which to update the widget.

        Any unset parameters will retain their previous value.

        """
        data = {'kind': 'textarea',
                'text': text or self.text,
                'shortName': short_name or self.shortName}
        self._update(data)
