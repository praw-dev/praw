"""Provide the SubredditWidgetsModeration class."""

import os.path
from json import dumps

from ....const import API_PATH


from .encoder import WidgetEncoder
from .widget.widget import Widget


class SubredditWidgetsModeration:
    """Class for moderating a subreddit's widgets.

    Get an instance of this class from :attr:`.SubredditWidgets.mod`.

    Example usage:

    .. code-block:: python

       styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
       reddit.subreddit('learnpython').widgets.mod.add_text_area(
           'My title', '**bold text**', styles)

    .. note::

       To use this class's methods, the authenticated user must be a moderator
       with appropriate permissions.
    """

    def __init__(self, subreddit, reddit):
        """Initialize the class."""
        self._subreddit = subreddit
        self._reddit = reddit

    def _create_widget(self, payload):
        path = API_PATH["widget_create"].format(subreddit=self._subreddit)
        widget = self._reddit.post(
            path, data={"json": dumps(payload, cls=WidgetEncoder)}
        )
        widget.subreddit = self._subreddit
        return widget

    def add_button_widget(
        self, short_name, description, buttons, styles, **other_settings
    ):
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
                       'text': 'ecruos weiV',
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
        button_widget = {
            "buttons": buttons,
            "description": description,
            "kind": "button",
            "shortName": short_name,
            "styles": styles,
        }
        button_widget.update(other_settings)
        return self._create_widget(button_widget)

    def add_calendar(
        self,
        short_name,
        google_calendar_id,
        requires_sync,
        configuration,
        styles,
        **other_settings
    ):
        """Add and return a :class:`.Calendar` widget.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param google_calendar_id: An email-style calendar ID. To share a
                                   Google Calendar, make it public,
                                   then find the "Calendar ID."
        :param requires_sync: A ``bool``.
        :param configuration: A ``dict`` as specified in `Reddit docs`_.

                              For example:

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
        calendar = {
            "shortName": short_name,
            "googleCalendarId": google_calendar_id,
            "requiresSync": requires_sync,
            "configuration": configuration,
            "styles": styles,
            "kind": "calendar",
        }
        calendar.update(other_settings)
        return self._create_widget(calendar)

    def add_community_list(
        self, short_name, data, styles, description="", **other_settings
    ):
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
        :param description: A ``str`` containing Markdown (default: ``''``).

        Example usage:

        .. code-block:: python

           widget_moderation = reddit.subreddit('mysub').widgets.mod
           styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
           subreddits = ['learnpython', reddit.subreddit('redditdev')]
           new_widget = widget_moderation.add_community_list('My fav subs',
                                                             subreddits,
                                                             styles,
                                                             'description')

        """
        community_list = {
            "data": data,
            "kind": "community-list",
            "shortName": short_name,
            "styles": styles,
            "description": description,
        }
        community_list.update(other_settings)
        return self._create_widget(community_list)

    def add_custom_widget(
        self,
        short_name,
        text,
        css,
        height,
        image_data,
        styles,
        **other_settings
    ):
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

            For example:

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
        custom_widget = {
            "css": css,
            "height": height,
            "imageData": image_data,
            "kind": "custom",
            "shortName": short_name,
            "styles": styles,
            "text": text,
        }
        custom_widget.update(other_settings)
        return self._create_widget(custom_widget)

    def add_image_widget(self, short_name, data, styles, **other_settings):
        r"""Add and return an :class:`.ImageWidget`.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param data: A ``list`` of ``dict``\ s as specified in `Reddit docs`_.
            Each ``dict`` has the key ``'url'`` which maps to the URL
            of an image hosted on Reddit's servers. Images should
            be uploaded using :meth:`.upload_image`.

            For example:

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
        image_widget = {
            "data": data,
            "kind": "image",
            "shortName": short_name,
            "styles": styles,
        }
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
        menu = {"data": data, "kind": "menu"}
        menu.update(other_settings)
        return self._create_widget(menu)

    def add_post_flair_widget(
        self, short_name, display, order, styles, **other_settings
    ):
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
           new_widget = widget_moderation.add_post_flair_widget('Some flairs',
                                                                'list',
                                                                flairs, styles)

        """
        post_flair = {
            "kind": "post-flair",
            "display": display,
            "shortName": short_name,
            "order": order,
            "styles": styles,
        }
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
        text_area = {
            "shortName": short_name,
            "text": text,
            "styles": styles,
            "kind": "textarea",
        }
        text_area.update(other_settings)
        return self._create_widget(text_area)

    def reorder(self, new_order, section="sidebar"):
        """Reorder the widgets.

        :param new_order: A list of widgets. Represented as a ``list`` that
            contains ``Widget`` objects, or widget IDs as strings. These types
            may be mixed.
        :param section: The section to reorder. (default: ``'sidebar'``)

        Example usage:

        .. code-block:: python

           widgets = reddit.subreddit('mysub').widgets
           order = list(widgets.sidebar)
           order.reverse()
           widgets.mod.reorder(order)

        """
        order = [
            thing.id if isinstance(thing, Widget) else str(thing)
            for thing in new_order
        ]
        path = API_PATH["widget_order"].format(
            subreddit=self._subreddit, section=section
        )
        self._reddit.patch(
            path, data={"json": dumps(order), "section": section}
        )

    def upload_image(self, file_path):
        """Upload an image to Reddit and get the URL.

        :param file_path: The path to the local file.
        :returns: The URL of the uploaded image as a ``str``.

        This method is used to upload images for widgets. For example,
        it can be used in conjunction with :meth:`.add_image_widget`,
        :meth:`.add_custom_widget`, and :meth:`.add_button_widget`.

        Example usage:

        .. code-block:: python

           my_sub = reddit.subreddit('my_sub')
           image_url = my_sub.widgets.mod.upload_image('/path/to/image.jpg')
           images = [{'width': 300, 'height': 300,
                      'url': image_url, 'linkUrl': ''}]
           styles = {'backgroundColor': '#FFFF66', 'headerColor': '#3333EE'}
           my_sub.widgets.mod.add_image_widget('My cool pictures', images,
                                               styles)
        """
        img_data = {
            "filepath": os.path.basename(file_path),
            "mimetype": "image/jpeg",
        }
        if file_path.lower().endswith(".png"):
            img_data["mimetype"] = "image/png"

        url = API_PATH["widget_lease"].format(subreddit=self._subreddit)
        # until we learn otherwise, assume this request always succeeds
        upload_lease = self._reddit.post(url, data=img_data)["s3UploadLease"]
        upload_data = {
            item["name"]: item["value"] for item in upload_lease["fields"]
        }
        upload_url = "https:{}".format(upload_lease["action"])

        with open(file_path, "rb") as image:
            response = self._reddit._core._requestor._http.post(
                upload_url, data=upload_data, files={"file": image}
            )
        response.raise_for_status()

        return upload_url + "/" + upload_data["key"]
