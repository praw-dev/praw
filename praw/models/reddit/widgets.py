"""Provide classes related to widgets."""

import os.path
from json import JSONEncoder, dumps
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypeVar, Union
from warnings import warn

from ...const import API_PATH
from ...util.cache import cachedproperty
from ..base import PRAWBase
from ..list.base import BaseList

if TYPE_CHECKING:  # pragma: no cover
    from .subreddit import Subreddit
    from ... import Reddit

_T = TypeVar("_T")


class WidgetBase(PRAWBase):
    """A PRAWBase that converts string RGB values into integers."""

    @staticmethod
    def _convert_rgb_string_to_int(string: str) -> Union[str, int]:
        """Convert a string RGB hex (#XXXXXX) to the integer representation.

        If the string is not an RGB code, returns the original string.

        :param string: The string to convert
        :returns: The converted value
        """
        if string.startswith("#") and len(string) == 7:
            return int(string[1:], 16)
        return string

    def __eq__(self: _T, other: _T) -> bool:
        """Compare another WidgetBase for equality."""
        if isinstance(other, type(self)):
            self_data = {
                name: value
                for name, value in vars(self).items()
                if not name.startswith("_")
            }
            other_data = {
                name: value
                for name, value in vars(other).items()
                if not name.startswith("_")
            }
            return self_data == other_data
        return super().__eq__(other)

    def __setattr__(self, name: str, value: Union[str, Dict[str, str]]):
        """Convert RGB values (#XXXXXX) to int and objectify styles."""
        if hasattr(self, "_reddit"):
            if isinstance(value, str) and self._reddit.config.widgets_beta:
                value = self._convert_rgb_string_to_int(value)
            if name == "styles" and self._reddit.config.widgets_beta:
                value = Styles(self._reddit, value)
        super().__setattr__(name, value)


class Button(WidgetBase):
    """Class to represent a single button inside a :class:`.ButtonWidget`.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``color``               The hex color used to outline the button.
    ``fillColor``           The hex color for the background of the button.
    ``textColor``           The hex color for the text of the button.
    ``height``              Image height. Only present on image buttons.
    ``hoverState``          A ``dict`` describing the state of the button when
                            hovered over. Optional.
    ``kind``                Either ``"text"`` or ``"image"``.
    ``linkUrl``             A link that can be visited by clicking the button.
                            Only present on image buttons.
    ``text``                The text displayed on the button.
    ``url``                 If the button is a text button, a link that can be
                            visited by clicking the button.

                            If the button is an image button, the URL of a
                            Reddit-hosted image.
    ``width``               Image width. Only present on image buttons.
    ======================= ===================================================
    """

    def __setattr__(self, name: str, value: Union[str, Dict[str, str]]):
        """Objectify ``hoverState``."""
        if hasattr(self, "_reddit"):
            if (
                name == "hoverState"
                and isinstance(value, dict)
                and self._reddit.config.widgets_beta
            ):
                value = Hover(self._reddit, value)
        super().__setattr__(name, value)


class CalendarConfiguration(WidgetBase):
    """Class to represent the configuration of a :class:`.Calendar`.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``numEvents``           The number of events to display on the calendar.
    ``showDate``            Whether or not to show the dates of events.
    ``showDescription``     Whether or not to show the descriptions of events.
    ``showLocation``        Whether or not to show the locations of events.
    ``showTime``            Whether or not to show the times of events.
    ``showTitle``           Whether or not to show the titles of events.
    ======================= ===================================================
    """


class Hover(WidgetBase):
    """Class to represent the hover data for a :class:`.ButtonWidget`.

    These values will take effect when the button is hovered over (the user
    moves their cursor so it's on top of the button).

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``color``               The hex color used to outline the button.
    ``fillColor``           The hex color for the background of the button.
    ``textColor``           The hex color for the text of the button.
    ``height``              Image height. Only present on image buttons.
    ``kind``                Either ``text`` or ``image``.
    ``text``                The text displayed on the button.
    ``url``                 If the button is an image button, the URL of a
                            Reddit-hosted image.
    ``width``               Image width. Only present on image buttons.
    ======================= ===================================================
    """


class Image(WidgetBase):
    """Class to represent an image that's part of a :class:`.ImageWidget`.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``height``              Image height.
    ``linkUrl``             A link that can be visited by clicking the image.
    ``url``                 The URL of the (Reddit-hosted) image.
    ``width``               Image width.
    ======================= ===================================================
    """


class ImageData(WidgetBase):
    """Class for image data that's part of a :class:`.CustomWidget`.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``height``              The image height.
    ``name``                The image name.
    ``url``                 The URL of the image on Reddit's servers.
    ``width``               The image width.
    ======================= ===================================================
    """


class MenuLink(WidgetBase):
    """Class to represent a single link inside a menu or submenu.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``text``                The text of the menu link.
    ``url``                 The URL that the menu item links to.
    ======================= ===================================================
    """


class Styles(WidgetBase):
    """Class to represent the style information of a widget.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``backgroundColor``     The background color of a widget, given as a
                            hexadecimal (``0x######``).
    ``headerColor``         The header color of a widget, given as a
                            hexadecimal (``0x######``).
    ======================= ===================================================

    **Working with Hexes**

    All color values are converted to the integer representation, so the string
    ``"#FFFFFF"`` is converted to ``0xFFFFFF``, which results in the integer
    ``16777215``. :class:`.Styles` provides two methods,
    :meth:`.convert_rgb_int_to_string` and :meth:`.convert_rgb_string_to_int`,
    for converting between the integer and the string representations.
    """

    @staticmethod
    def convert_rgb_int_to_string(integer: int) -> str:
        """Convert an integer representation of an RGB code to a string.

        :param integer: The integer to convert. Must be greater than or equal
            to ``0`` and less than or equal to ``16777215`` (``0xFFFFFF``).
        :raises: :py:class:`ValueError` if the integer is out of bounds.
        :returns: The string version of the integer.

        .. seealso:: :meth:`.convert_rgb_string_to_int`
        """
        if not (0x000000 <= integer <= 0xFFFFFF):
            raise ValueError(
                "The given integer ({}) is greater than 16777215 or less than "
                "0.".format(integer)
            )
        return "#{}".format(hex(integer)[2:])

    @classmethod
    def convert_rgb_string_to_int(cls, string: str) -> int:
        """Convert the string representation of an RGB code to an integer.

        :param string: The string to convert to an integer.
        :raises: :py:class:`.ValueError` if the string is not provided in the
            appropriate format (``"#XXXXXX"`` where ``X`` represents a
            character).
        :returns: The integer representation of the string.

        .. seealso:: :meth:`.convert_rgb_int_to_string`
        """
        value = cls._convert_rgb_string_to_int(string)
        if isinstance(value, str):
            raise ValueError(
                "An hxadecimal string ``#XXXXXX`` was not specified, instead "
                "{!r} was specified".format(string)
            )
        return value


class Submenu(BaseList):
    r"""Class to represent a submenu of links inside a menu.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``children``            A list of the :class:`.MenuLink`\ s in this
                            submenu. Can be iterated over by iterating over the
                            :class:`.Submenu` (e.g. ``for menu_link in
                            submenu``).
    ``text``                The name of the submenu.
    ======================= ===================================================
    """

    CHILD_ATTRIBUTE = "children"


class SubredditWidgets(PRAWBase):
    """Class to represent a subreddit's widgets.

    Create an instance like so:

    .. code-block:: python

       widgets = reddit.subreddit("redditdev").widgets

    Data will be lazy-loaded. By default, PRAW will not request progressively
    loading images from Reddit. To enable this, instantiate a SubredditWidgets
    object, then set the attribute ``progressive_images`` to ``True`` before
    performing any action that would result in a network request.

    .. code-block:: python

       widgets = reddit.subreddit("redditdev").widgets
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

       widgets.mod.add_text_area("My title", "**bold text**",
                                 {"backgroundColor": "#FFFF66",
                                  "headerColor": "#3333EE"})

    For more information, see :class:`.SubredditWidgetsModeration`.

    To edit a particular widget, use ``.mod`` on the widget. For example:

    .. code-block:: python

       for widget in widgets.sidebar:
           widget.mod.update(shortName="Exciting new name")

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
    def id_card(self) -> "IDCard":
        """Get this subreddit's :class:`.IDCard` widget."""
        return self.items[self.layout["idCardWidget"]]

    @cachedproperty
    def items(self) -> Dict[str, "Widget"]:
        """Get this subreddit's widgets as a dict from ID to widget."""
        items = {}
        for item_name, data in self._raw_items.items():
            data["subreddit"] = self.subreddit
            items[item_name] = self._reddit._objector.objectify(data)
        return items

    @cachedproperty
    def mod(self) -> "SubredditWidgetsModeration":
        """Get an instance of :class:`.SubredditWidgetsModeration`.

        .. note::

           Using any of the methods of :class:`.SubredditWidgetsModeration`
           will likely result in the data of this :class:`.SubredditWidgets`
           being outdated. To re-sync, call :meth:`.refresh`.
        """
        return SubredditWidgetsModeration(self.subreddit, self._reddit)

    @cachedproperty
    def moderators_widget(self) -> "ModeratorsWidget":
        """Get this subreddit's :class:`.ModeratorsWidget`."""
        return self.items[self.layout["moderatorWidget"]]

    @cachedproperty
    def sidebar(self) -> List["Widget"]:
        """Get a list of Widgets that make up the sidebar."""
        return [
            self.items[widget_name]
            for widget_name in self.layout["sidebar"]["order"]
        ]

    @cachedproperty
    def topbar(self) -> List["Widget"]:
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

           widgets = reddit.subreddit("redditdev").widgets
           widgets.progressive_images = True
           widgets.refresh()

        """
        self._fetch()

    def __getattr__(self, attr: str) -> Any:
        """Return the value of `attr`."""
        if not attr.startswith("_") and not self._fetched:
            self._fetch()
            return getattr(self, attr)
        raise AttributeError(
            "{!r} object has no attribute {!r}".format(
                self.__class__.__name__, attr
            )
        )

    def __init__(self, subreddit: "Subreddit"):
        """Initialize the class.

        :param subreddit: The :class:`.Subreddit` the widgets belong to.

        """
        self._raw_items = None
        self._fetched = False
        self.subreddit = subreddit
        self.progressive_images = False

        super().__init__(subreddit._reddit, None)

    def __repr__(self) -> str:
        """Return an object initialization representation of the object."""
        return "SubredditWidgets(subreddit={!r})".format(self.subreddit)

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


class SubredditWidgetsModeration:
    """Class for moderating a subreddit's widgets.

    Get an instance of this class from :attr:`.SubredditWidgets.mod`.

    Example usage:

    .. code-block:: python

       styles =
       styles = {"backgroundColor": "#FFFF66", "headerColor": "#3333EE"}
       reddit.subreddit("learnpython").widgets.mod.add_text_area(
           "My title", "**bold text**", )

    .. note::

       To use this class's methods, the authenticated user must be a moderator
       with appropriate permissions.
    """

    @classmethod
    def _convert_color_list_to_RGB(
        cls,
        data: List[
            Union[Dict[str, Union[int, Dict[str, int]]], List[Dict[str, int]]]
        ],
    ) -> List[
        Union[Dict[str, Union[str, Dict[str, str]]], List[Dict[str, str]]]
    ]:
        """Iterate through a list, converting any lists and dicitonaries.

        :param data: The data to convert
        :returns: A list with the converted values
        """
        converted = []
        for item in data:
            if isinstance(item, dict):
                converted.append(cls._convert_color_to_RGB(item))
            elif isinstance(item, list):
                converted.append(cls._convert_color_list_to_RGB(item))
            else:
                converted.append(item)
        return converted

    @classmethod
    def _convert_color_to_RGB(
        cls, data: Dict[str, Union[int, List[Any], Dict[str, Any], Any]]
    ) -> Dict[str, Union[str, Any]]:
        """Iterate through a dictionary, converting color keys to RGB strings.

        :param data: The data to convert
        :returns: A dictionary with the converted values

        For example, given the dict below:

        .. code-block:: python

            data = {"buttons": [{"color": 16777215, "text": "Hello World!"},
                    {"color": 0, "url": "https://www.google.com"}],
                "backgroundColor": 65280}

        When run through the converter, results in:

        .. code-block:: python

            data = {"buttons": [{"color": "#FFFFFF", "text": "Hello World!"},
                    {"color": "#000000", "url": "https://www.google.com"}],
                "backgroundColor": "#00FF00"}

        """
        converted = {}
        for key, value in data.items():
            if isinstance(value, dict):
                converted[key] = cls._convert_color_to_RGB(value)
            elif isinstance(value, list):
                converted[key] = cls._convert_color_list_to_RGB(value)
            elif "color" in key.lower() and isinstance(value, int):
                val = "#{}".format(hex(value)[2:])
                while len(val) < 7:
                    val = "#0" + val[1:]
                converted[key] = val
            else:
                converted[key] = value
        return converted

    def __init__(self, subreddit: "Subreddit", reddit: "Reddit"):
        """Initialize the class."""
        self._subreddit = subreddit
        self._reddit = reddit

    def _create_widget(
        self, payload: Dict[str, Union[str, Any]]
    ) -> Union[
        "ButtonWidget",
        "Calendar",
        "CommunityList",
        "CustomWidget",
        "ImageWidget",
        "Menu",
        "PostFlairWidget",
        "TextArea",
    ]:
        path = API_PATH["widget_create"].format(subreddit=self._subreddit)
        data = self._convert_color_to_RGB(
            {"json": dumps(payload, cls=WidgetEncoder)}
        )
        widget = self._reddit.post(path, data=data,)
        widget.subreddit = self._subreddit
        return widget

    def add_button_widget(
        self,
        short_name: str,
        description: str,
        buttons: List[Button],
        styles: Styles,
        **other_settings: str
    ) -> "ButtonWidget":
        """Add and return a :class:`.ButtonWidget`.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param description: Markdown text to describe the widget.
        :param buttons: A ``list`` of instances of :class:`.Button`, generated
            with :meth:`.generate_button`.
        :param styles: An instance of :class:`.Styles`, generated with
            :meth:`.generate_styles`.

        Example usage:

        .. code-block:: python

            widget_moderation = reddit.subreddit("mysub").widgets.mod
            my_image = widget_moderation.upload_image("/path/to/pic.jpg")
            buttons = [
                widget_moderation.generate_button("text", "View source",
                    "https://github.com/praw-dev/praw", color=0xFF0000,
                    textColor=0x00FF00, fillColor=0x0000FF,
                    hover=widget_moderation.generate_hover("text",
                        text="ecruos weiV", color=0xFFFFFF, textColor=0x000000,
                        fillColor=0x0000FF)),
                widget_moderation.generate_button("image",
                    "View documentation", my_image,
                    linkUrl="https://praw.readthedocs.io", height=200,
                    width=200,
                    hover=widget_moderation.generate_hover("image",
                        url=my_image, height=200, width=200)
                    )
            ]
            styles = widget_moderation.generate_styles(0xFFFF66, 0x3333EE)
            new_widget = widget_moderation.add_button_widget(
                "Things to click", "Click some of these *cool* links!",
                buttons, styles)

        .. note:: Porting code is relatively simple. Dictionary keys can become
            function keywords by putting ``**`` before the variable holding
            the dictionary. For example, the list below:

            .. code-block:: python

                button_1 = {
                    "kind": "text",
                    "text": "View source",
                    "url": 'https://github.com/praw-dev/praw',
                    "color": "#FF0000",
                    "textColor": "#00FF00",
                    "fillColor": "#0000FF",
                    "hoverState": {
                        "kind": "text",
                        "text": "ecruos weiV",
                        "color": "#FFFFFF",
                        "textColor": "#000000",
                        "fillColor": "#0000FF"
                    }
                }
                button_2 = {
                    "kind": "image",
                    "text": "View documentation",
                    "linkUrl": 'https://praw.readthedocs.io',
                    "url": my_image,
                    "height": 200,
                    "width": 200,
                    "hoverState": {
                        "kind": "image",
                        "url": my_image,
                        "height": 200,
                        "width": 200
                    }
                }
                buttons = [button_1, button_2]

            For each button, it is possible to replace the ``hoverState`` key
            with an instance of :class:`.Hover` using ``**``, like so:

            .. code-block:: python

                widget_mod = reddit.subreddit("test").widgets.mod
                button_1 = {
                    "kind": "text",
                    "text": "View source",
                    "url": 'https://github.com/praw-dev/praw',
                    "color": "#FF0000",
                    "textColor": "#00FF00",
                    "fillColor": "#0000FF",
                    "hoverState": widget_mod.generate_hover(**{
                        "kind": "text",
                        "text": "ecruos weiV",
                        "color": "#FFFFFF",
                        "textColor": "#000000",
                        "fillColor": "#0000FF"
                    })
                }
                button_2 = {
                    "kind": "image",
                    "text": "View documentation",
                    "linkUrl": 'https://praw.readthedocs.io',
                    "url": my_image,
                    "height": 200,
                    "width": 200,
                    "hoverState": widget_mod.generate_hover(**{
                        "kind": "image",
                        "url": my_image,
                        "height": 200,
                        "width": 200
                    })
                }

            Once all of the hover states have been converted, we can do the
            same with the buttons themselves, like so:

            .. code-block:: python

                widget_mod = reddit.subreddit("test").widgets.mod
                button_1 = {
                    "kind": "text",
                    "text": "View source",
                    "url": 'https://github.com/praw-dev/praw',
                    "color": "#FF0000",
                    "textColor": "#00FF00",
                    "fillColor": "#0000FF",
                    "hoverState": widget_mod.generate_hover(**{
                        "kind": "text",
                        "text": "ecruos weiV",
                        "color": "#FFFFFF",
                        "textColor": "#000000",
                        "fillColor": "#0000FF"
                    })
                }
                button_2 = {
                    "kind": "image",
                    "text": "View documentation",
                    "linkUrl": 'https://praw.readthedocs.io',
                    "url": my_image,
                    "height": 200,
                    "width": 200,
                    "hoverState": widget_mod.generate_hover(**{
                        "kind": "image",
                        "url": my_image,
                        "height": 200,
                        "width": 200
                    })
                }
                buttons = [widget_mod.generate_button(**button_1),
                    widget_mod.generate_button(**button_2)
                ]
        """
        for button in buttons:
            if isinstance(button, dict):
                warn(
                    "Providing a list of dictionaries for the ``buttons`` "
                    "parameter is deprecated. Please replace the dictionary "
                    "with a call to widgets.mod.generate_button. See the "
                    "documentation for the add_button_widget method at "
                    "https://praw.readthedocs.io/en/latest/code_overview/other"
                    "/subredditwidgetsmoderation.html#praw.models.SubredditWid"
                    "getsModeration.add_button_widget on how to port code.",
                    category=DeprecationWarning,
                    stacklevel=2,
                )
        if isinstance(styles, dict):
            warn(
                "Providing a dictionary for the ``styles`` parameter is "
                "deprecated. Please replace the dictionary with a call to "
                "widgets.mod.generate_styles. See the documentation for the "
                "generate_styles method at https://praw.readthedocs.io/en/"
                "latest/code_overview/other/subredditwidgetsmoderation.html"
                "#praw.models.SubredditWidgetsModeration.generate_styles on "
                "how to port code.",
                category=DeprecationWarning,
                stacklevel=2,
            )
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
        short_name: str,
        google_calendar_id: str,
        requires_sync: bool,
        configuration: CalendarConfiguration,
        styles: Styles,
        **other_settings: str
    ) -> "Calendar":
        """Add and return a :class:`.Calendar` widget.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param google_calendar_id: An email-style calendar ID. To share a
            Google Calendar, make it public, then find the "Calendar ID."
        :param requires_sync: A ``bool`` representing whether or not the
            calender needs to be synced.
        :param configuration: An instance of :class:`.CalendarConfiguration`.
        :param styles: An instance of :class:`.Styles`, generated with
            :meth:`.generate_styles`.

        Example usage:

        .. code-block:: python

            widget_moderation = reddit.subreddit("mysub").widgets.mod
            styles = widget_moderation.generate_styles(0xFFFF66, 0x3333EE)
            config = widget_moderation.generate_calendar_configuration(
                numEvents=10, showDate=True, showDescription=False,
                showLocation=False, showTime=True, showTitle=True)
            cal_id = "y6nm89jy427drk8l71w75w9wjn@group.calendar.google.com"
            new_widget = widget_moderation.add_calendar("Upcoming Events",
                cal_id, True, config, styles)

        .. note:: Porting code is relatively simple with the ``**`` dictionary
            keyword argument. For example, given the dict below:

            .. code-block:: python

                config = {"numEvents": 10,
                    "showDate": True,
                    "showDescription": False,
                    "showLocation": False,
                    "showTime": True,
                    "showTitle": True
                }

            Using the ``**`` parameter, the dict can be converted to an
            instance of :class:`.CalendarConfiguration`, like so:

            .. code-block:: python

                widget_mod = reddit.subreddit("test").widgets.mod
                config = widget_mod.generate_calendar_configuration(**{
                    "numEvents": 10,
                    "showDate": True,
                    "showDescription": False,
                    "showLocation": False,
                    "showTime": True,
                    "showTitle": True
                })
        """
        if isinstance(configuration, dict):
            warn(
                "Providing a dictionary for the ``configuration`` parameter is"
                " deprecated. Please replace the dictionary with a call to "
                "widgets.mod.generate_calendar_configuration. See the "
                "documentation for the add_calendar method at https://praw."
                "readthedocs.io/en/latest/code_overview/other/subredditwidget"
                "smoderation.html#praw.models.SubredditWidgetsModeration.add"
                "_calendar on how to port code.",
                category=DeprecationWarning,
                stacklevel=2,
            )
        if isinstance(styles, dict):
            warn(
                "Providing a dictionary for the ``styles`` parameter is "
                "deprecated. Please replace the dictionary with a call to "
                "widgets.mod.generate_styles. See the documentation for the "
                "generate_styles method at https://praw.readthedocs.io/en/"
                "latest/code_overview/other/subredditwidgetsmoderation.html"
                "#praw.models.SubredditWidgetsModeration.generate_styles on "
                "how to port code.",
                category=DeprecationWarning,
                stacklevel=2,
            )
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
        self,
        short_name: str,
        data: List[Union[str, "Subreddit"]],
        styles: Styles,
        description: str = "",
        **other_settings: str
    ) -> "CommunityList":
        """Add and return a :class:`.CommunityList` widget.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param data: A ``list`` of subreddits. Subreddits can be represented as
            strings or instances of :class:`.Subreddit`.
        :param styles: An instance of :class:`.Styles`, generated with
            :meth:`.generate_styles`.
        :param description: A string containing Markdown (default: ``""``).

        Example usage:

        .. code-block:: python

            widget_moderation = reddit.subreddit("mysub").widgets.mod
            styles = widget_moderation.generate_styles(0xFFFF66, 0x3333EE)
            subreddits = ["learnpython", reddit.subreddit("redditdev")]
            new_widget = widget_moderation.add_community_list("My fav subs",
                subreddits, styles, "description")

        """
        if isinstance(styles, dict):
            warn(
                "Providing a dictionary for the ``styles`` parameter is "
                "deprecated. Please replace the dictionary with a call to "
                "widgets.mod.generate_styles. See the documentation for the "
                "generate_styles method at https://praw.readthedocs.io/en/"
                "latest/code_overview/other/subredditwidgetsmoderation.html"
                "#praw.models.SubredditWidgetsModeration.generate_styles on "
                "how to port code.",
                category=DeprecationWarning,
                stacklevel=2,
            )
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
        short_name: str,
        text: str,
        css: str,
        height: int,
        image_data: List[ImageData],
        styles: Styles,
        **other_settings: str
    ) -> "CustomWidget":
        """Add and return a :class:`.CustomWidget`.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param text: The Markdown text displayed in the widget.
        :param css: The CSS for the widget, no longer than 100000 characters.

            .. note:: As of this writing, Reddit will not accept empty CSS. If
                you wish to create a custom widget without CSS, consider using
                ``"/**/"`` (an empty comment) as your CSS.

        :param height: The height of the widget, between 50 and 500.
        :param image_data: A ``list`` of instances of :class:`.ImageData`.
        :param styles: An instance of :class:`.Styles`, generated with
            :meth:`.generate_styles`.

        Example usage:

        .. code-block:: python

            widget_moderation = reddit.subreddit("mysub").widgets.mod
            image_url1 = widget_moderation.upload_image("/path/to/image1.jpg")
            image_url2 = widget_moderation.upload_image("/path/to/image2.jpg")
            image1 = widget_moderation.generate_image_data(image_url1, 600,
                450, "logo")
            image2 = widget_moderation.generate_image_data(image_url2, 450,
                600, "icon")
            images = [image1, image2]
            styles = widget_moderation.generate_styles(0xFFFF66, 0x3333EE)
            new_widget = widget_moderation.add_custom_widget("My widget",
                "# Hello world!", "/**/", 200, images, styles)

        .. note:: Porting code is relatively simple with the ``**`` dictionary
            keyword argument. For example, given the list of dicts below:

            .. code-block:: python

                image_paths = ["/path/to/image1.jpg", "/path/to/image2.png"]
                image_urls = [widget_moderation.upload_image(img_path)
                    for img_path in image_paths]
                image_dicts = [
                    {"width": 600, "height": 450, "name": "logo",
                    "url": image_urls[0]},
                    {"width": 450, "height": 600, "name": "icon",
                    "url": image_urls[1]}
                ]

            Using the ``**`` argument, the dictionaries can be converted to
            instances of :class:`.ImageData`, like so:

            .. code-block:: python

                widget_mod = reddit.subreddit("test").widgets.mod
                image_paths = ["/path/to/image1.jpg", "/path/to/image2.png"]
                image_urls = [widget_mod.upload_image(img_path)
                    for img_path in image_paths]
                image_dicts = [
                    widget_mod.generate_image_data(**{
                    "width": 600, "height": 450, "name": "logo",
                    "url": image_urls[0]}),
                    widget_mod.generate_image_data(**{
                    "width": 450, "height": 600, "name": "icon",
                    "url": image_urls[1]})
                ]
        """
        for item in image_data:
            if isinstance(item, dict):
                warn(
                    "Providing a list of dictionaries for the ``image_data`` "
                    "parameter is deprecated. Please replace the dictionaries "
                    "with calls to widgets.mod.generate_image_data. See the "
                    "documentation for the add_custom_widget method at "
                    "https://praw.readthedocs.io/en/latest/code_overview"
                    "/other/subredditwidgetsmoderation.html#praw.models"
                    ".SubredditWidgetsModeration.add_custom_widget on how to "
                    "port code.",
                    category=DeprecationWarning,
                    stacklevel=2,
                )
        if isinstance(styles, dict):
            warn(
                "Providing a dictionary for the ``styles`` parameter is "
                "deprecated. Please replace the dictionary with a call to "
                "widgets.mod.generate_styles. See the documentation for the "
                "generate_styles method at https://praw.readthedocs.io/en/"
                "latest/code_overview/other/subredditwidgetsmoderation.html"
                "#praw.models.SubredditWidgetsModeration.generate_styles on "
                "how to port code.",
                category=DeprecationWarning,
                stacklevel=2,
            )
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

    def add_image_widget(
        self,
        short_name: str,
        data: List[Image],
        styles: Styles,
        **other_settings: str
    ) -> "ImageWidget":
        r"""Add and return an :class:`.ImageWidget`.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param data: A ``list`` of instances of :class:`.Image`.
        :param styles: An instance of :class:`.Styles`, generated with
            :meth:`.generate_styles`.

        Example usage:

        .. code-block:: python

            widget_moderation = reddit.subreddit("mysub").widgets.mod
            image_paths = ["/path/to/image1.jpg", "/path/to/image2.png"]
            images = [widget_moderation.generate_image(
                widget_moderation.upload_image(img_path), 600, 450)
                for img_path in image_paths]
            styles = widget_moderation.generate_styles(0xFFFF66, 0x3333EE)
            new_widget = widget_moderation.add_image_widget("My cool pictures",
                images, styles)

        .. note:: Porting code is relatively simple with the ``**`` dictionary
            keyword argument. For example, given the list of dicts below:

            .. code-block:: python

                data = [{"url": 'https://some.link',  # from upload_image()
                 "width": 600, "height": 450,
                 "linkUrl": 'https://github.com/praw-dev/praw'},
                {"url": 'https://other.link',  # from upload_image()
                 "width": 450, "height": 600,
                 "linkUrl": 'https://praw.readthedocs.io'}]

            Using the ``**`` argument, the dictionaries can be converted to
            instances of :class:`.Image`, like so:

            .. code-block:: python

                widget_mod = reddit.subreddit("test").widgets.mod
                data = [
                widget_mod.generate_image(**{
                    "url": 'https://some.link',  # from upload_image()
                    "width": 600, "height": 450,
                    "linkUrl": 'https://github.com/praw-dev/praw'}),
                widget_mod.generate_image(**{
                    "url": 'https://other.link',  # from upload_image()
                    "width": 450, "height": 600,
                    "linkUrl": 'https://praw.readthedocs.io'})
                ]
        """
        for item in data:
            if isinstance(item, dict):
                warn(
                    "Providing a list of dictionaries for the ``data`` "
                    "parameter is deprecated. Please replace the dictionaries "
                    "with calls to widgets.mod.generate_image. See the "
                    "documentation for the add_image_widget method at "
                    "https://praw.readthedocs.io/en/latest/code_overview"
                    "/other/subredditwidgetsmoderation.html#praw.models"
                    ".SubredditWidgetsModeration.add_image_widget on how to "
                    "port code.",
                    category=DeprecationWarning,
                    stacklevel=2,
                )
        if isinstance(styles, dict):
            warn(
                "Providing a dictionary for the ``styles`` parameter is "
                "deprecated. Please replace the dictionary with a call to "
                "widgets.mod.generate_styles. See the documentation for the "
                "generate_styles method at https://praw.readthedocs.io/en/"
                "latest/code_overview/other/subredditwidgetsmoderation.html"
                "#praw.models.SubredditWidgetsModeration.generate_styles on "
                "how to port code.",
                category=DeprecationWarning,
                stacklevel=2,
            )
        image_widget = {
            "data": data,
            "kind": "image",
            "shortName": short_name,
            "styles": styles,
        }
        image_widget.update(other_settings)
        return self._create_widget(image_widget)

    def add_menu(
        self, data: List[Union[MenuLink, Submenu]], **other_settings: str
    ) -> "Menu":
        r"""Add and return a :class:`.Menu` widget.

        :param data: A ``list`` of instances of :class:`.MenuLink` and/or
            :class:`.Submenu`.

        Example usage:

        .. code-block:: python

            widget_moderation = reddit.subreddit("mysub").widgets.mod
            menu_contents = [
                widget_moderation.generate_menu_link(
                    "Reddit Homepage", "https://www.reddit.com"
                ),
                widget_moderation.generate_submenu(
                    [
                        widget_moderation.generate_menu_link(
                            "PRAW", "https://praw.readthedocs.io/"
                        ),
                        widget_moderation.generate_menu_link(
                            "requests", "https://requests.readthedocs.io/"
                        ),
                    ],
                    "Python packages",
                ),
                widget_moderation.generate_menu_link(
                    "Reddit Homepage", "https://www.reddit.com"
                )]
            new_widget = widget_moderation.add_menu(menu_contents)

        .. note:: Porting code is relatively simple with the ``**`` dictionary
            keyword argument. For example, given the list of dicts below:

            .. code-block:: python

                menu_contents = [
                    {"text": "My homepage", "url": 'https://example.com'},
                    {"text": "Python packages",
                    "children": [
                        {"text": "PRAW",
                        "url": 'https://praw.readthedocs.io/'},
                        {"text": "requests",
                        "url": 'http://python-requests.org'}
                    ]},
                    {"text": "Reddit homepage", "url": 'https://reddit.com'}
                ]

            Using the ``**`` argument, the dictionaries can be converted to
            instances of :class:`.MenuLink` and :class:`.Submenu`, like so:

            .. code-block:: python

                widget_mod = reddit.subreddit("test").widgets.mod
                menu_contents = [
                    widget_mod.generate_menu_link(**{
                        "text": "My homepage", "url": 'https://example.com'}),
                    widget_mod.generate_submenu(**{
                        "text": "Python packages",
                        "children": [
                            widget_mod.generate_menu_link(**{
                                "text": "PRAW",
                                "url": 'https://praw.readthedocs.io/'}),
                            widget_mod.generate_menu_link(**{
                                "text": "requests",
                                "url": 'http://python-requests.org'})
                        ]}),
                    widget_mod.generate_menu_link(**{
                        "text": "Reddit homepage",
                        "url": 'https://reddit.com'})
                ]
        """
        for item in data:
            if isinstance(item, dict):
                warn(
                    "Providing a list of dictionaries for the ``data`` "
                    "parameter is deprecated. Please replace the "
                    "dictionaries with calls to "
                    "widgets.mod.generate_menu_link and "
                    "widgets.mod.generate_submenu. See the documentation for "
                    "the add_menu method at "
                    "https://praw.readthedocs.io/en/latest/code_overview"
                    "/other/subredditwidgetsmoderation.html#praw.models"
                    ".SubredditWidgetsModeration.add_menu on how to port "
                    "code.",
                    category=DeprecationWarning,
                    stacklevel=2,
                )
        menu = {"data": data, "kind": "menu"}
        menu.update(other_settings)
        return self._create_widget(menu)

    def add_post_flair_widget(
        self,
        short_name: str,
        display: str,
        order: List[str],
        styles: Styles,
        **other_settings: str
    ) -> "PostFlairWidget":
        """Add and return a :class:`.PostFlairWidget`.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param display: Display style. Either ``"cloud"`` or ``"list"``.
        :param order: A ``list`` of flair template IDs. You can get all flair
            template IDs in a subreddit with:

            .. code-block:: python

               flairs = [f["id"] for f in subreddit.flair.link_templates]

        :param styles: An instance of :class:`.Styles`, generated with
            :meth:`.generate_styles`.

        Example usage:

        .. code-block:: python

            widget_moderation = reddit.subreddit("mysub").widgets.mod
            flairs = [f["id"] for f in subreddit.flair.link_templates]
            styles = widget_moderation.generate_styles(0xFFFF66, 0x3333EE)
            new_widget = widget_moderation.add_post_flair_widget("Some flairs",
                "list", flairs, styles)

        """
        if isinstance(styles, dict):
            warn(
                "Providing a dictionary for the ``styles`` parameter is "
                "deprecated. Please replace the dictionary with a call to "
                "widgets.mod.generate_styles. See the documentation for the "
                "generate_styles method at https://praw.readthedocs.io/en/"
                "latest/code_overview/other/subredditwidgetsmoderation.html"
                "#praw.models.SubredditWidgetsModeration.generate_styles on "
                "how to port code.",
                category=DeprecationWarning,
                stacklevel=2,
            )
        post_flair = {
            "kind": "post-flair",
            "display": display,
            "shortName": short_name,
            "order": order,
            "styles": styles,
        }
        post_flair.update(other_settings)
        return self._create_widget(post_flair)

    def add_text_area(
        self, short_name: str, text: str, styles: Styles, **other_settings: str
    ) -> "TextArea":
        """Add and return a :class:`.TextArea` widget.

        :param short_name: A name for the widget, no longer than 30 characters.
        :param text: The Markdown text displayed in the widget.
        :param styles: An instance of :class:`.Styles`, generated with
            :meth:`.generate_styles`.

        Example usage:

        .. code-block:: python

            widget_moderation = reddit.subreddit("mysub").widgets.mod
            styles = widget_moderation.generate_styles(0xFFFF66, 0x3333EE)
            new_widget = widget_moderation.add_text_area("My cool title",
                "*Hello* **world**!", styles)

        """
        if isinstance(styles, dict):
            warn(
                "Providing a dictionary for the ``styles`` parameter is "
                "deprecated. Please replace the dictionary with a call to "
                "widgets.mod.generate_styles. See the documentation for the "
                "generate_styles method at https://praw.readthedocs.io/en/"
                "latest/code_overview/other/subredditwidgetsmoderation.html"
                "#praw.models.SubredditWidgetsModeration.generate_styles on "
                "how to port code.",
                category=DeprecationWarning,
                stacklevel=2,
            )
        text_area = {
            "shortName": short_name,
            "text": text,
            "styles": styles,
            "kind": "textarea",
        }
        text_area.update(other_settings)
        return self._create_widget(text_area)

    def generate_button(
        self,
        kind: str,
        text: str,
        url: str,
        color: Optional[Union[str, int]] = None,
        fillColor: Optional[Union[str, int]] = None,
        height: Optional[int] = None,
        hoverState: Optional[Hover] = None,
        linkUrl: Optional[str] = None,
        textColor: Optional[Union[str, int]] = None,
        width: Optional[int] = None,
    ) -> Button:
        """Generate an instance of :class:`.Button`.

        This object should be used with :meth:`.add_button_widget` to create
        a button widget.

        :param kind: The type of button (``"image"`` or ``"text"``)
        :param text: The button text.
        :param url: The url of the button. On image buttons, ``url`` should be
            a link to the image obtained from :meth:`.upload_image`.
        :param color: The color of the button. Should either be given as a
            7-character RGB code (``"#FFFFFF"``) or the integer representation
            (``0xFFFFFF``).
        :param fillColor: The background color of the button. Should either be
            given as a 7-character RGB code (``"#FFFFFF"``) or the integer
            representation (``0xFFFFFF``).
        :param height: The height of the image, if the button is an image
            button.
        :param hoverState: An instance of :class:`.Hover` containing the hover
            data for the button. An instance of :class:`.Hover` can be obtained
            from :meth:`.generate_hover`. Optional.
        :param linkUrl: If the button is an image button, represents the link
            that the user will visit when the image is clicked on. Optional.
        :param textColor: The color of the button text. Should either be given
            as a 7-character RGB code (``"#FFFFFF"``) or the integer
            representation (``0xFFFFFF``).
        :param width: The width of the image, if the button is an image button.
        :returns: An instance of :class:`.Button`.

        For example, to generate a text button:

        .. code-block:: python

            widget_mod = reddit.subreddit("test").widgets.mod
            hover = widget_mod.generate_hover("text", color=0xFF0000,
                fillColor=0x000000, text="Don't click me", textColor=0xFFFFFF,
                url="https://www.reddit.com")
            button = widget_mod.generate_button("text", "Click me!",
                "https://www.google.com", color=0x00FF00, fillColor=0xFFFFFF,
                hoverState=hover, textColor=0x000000)

        To generate an image button:

        .. code-block:: python

            widget_mod = reddit.subreddit("test").widgets.mod
            image_1 = widget_mod.upload_image("image.png")
            image_2 = widget_mod.upload_image("image2.png")
            hover = widget_mod.generate_hover("image",
                linkUrl = "https://www.reddit.com", height=400
                text="Don't click me", url=image_2, width=200)
            button = widget_mod.generate_button("image", "Click me!", image_1,
                height = 200, hoverState = hover,
                linkUrl = "https://www.google.com", width=200)

        The hover states do not have to correspond to the given button types.

        .. code-block:: python

            widget_mod = reddit.subreddit("test").widgets.mod
            image_1 = widget_mod.upload_image("image.png")
            hover = widget_mod.generate_hover("text", color=0xFF0000,
                fillColor=0x000000, text="Don't click me", textColor=0xFFFFFF,
                url="https://www.reddit.com")
            button = widget_mod.generate_button("image", "Click me!", image_1,
                height = 200, hoverState=hover,
                linkUrl = "https://www.google.com", width=200)

        .. code-block:: python

            widget_mod = reddit.subreddit("test").widgets.mod
            image = widget_mod.upload_image("image.png")
            hover = widget_mod.generate_hover("image",
                linkUrl = "https://www.reddit.com", height=400
                text="Don't click me", url=image, width=200)
            button = widget_mod.generate_button("text", "Click me!",
                "https://www.google.com", color=0x00FF00, fillColor=0xFFFFFF,
                hoverState=hover, textColor=0x000000)
        """
        data = {"kind": kind, "text": text, "url": url}
        for name, value in {
            "color": color,
            "fillColor": fillColor,
            "height": height,
            "hoverState": hoverState,
            "linkUrl": linkUrl,
            "textColor": textColor,
            "width": width,
        }.items():
            if value is not None:
                data[name] = value
            if name == "hoverState" and isinstance(hoverState, dict):
                warn(
                    "Providing a dictionary for parameter ``hoverState`` is "
                    "deprecated. Please provide an instance of the Hover "
                    "class, which can be generated by the generate_hover"
                    " method. See the documentation for the add_button_widget "
                    "method at https://praw.readthedocs.io/en/latest/"
                    "code_overview/other/subredditwidgetsmoderation.html#praw"
                    ".models.SubredditWidgetsModeration.add_button_widget on "
                    "how to port code.",
                    category=DeprecationWarning,
                    stacklevel=2,
                )
        return Button(self._reddit, data)

    def generate_calendar_configuration(
        self,
        numEvents: int,
        showDate: bool,
        showDescription: bool,
        showLocation: bool,
        showTime: bool,
        showTitle: bool,
    ) -> CalendarConfiguration:
        """Generate an instance of :class:`.CalendarConfiguration`.

        This method should be used to generate an object for the
        ``configuration`` parameter of :meth:`.add_calendar`.

        :param numEvents: The number of events to show on the calendar.
        :param showDate: Show the date of events.
        :param showDescription: Show the description of events.
        :param showLocation: Show the location of events.
        :param showTime: Show the time of events.
        :param showTitle: Show the title of events.
        :returns: An instance of :class:`.CalendarConfiguration`

        Example usage:

        .. code-block:: python

            widget_moderation = reddit.subreddit("mysub").widgets.mod
            config = widget_moderation.generate_calendar_configuration(
                numEvents=10, showDate=True, showDescription=False,
                showLocation=False, showTime=True, showTitle=True)
        """
        return CalendarConfiguration(
            self._reddit,
            {
                "numEvents": numEvents,
                "showDate": showDate,
                "showDescription": showDescription,
                "showLocation": showLocation,
                "showTime": showTime,
                "showTitle": showTitle,
            },
        )

    def generate_hover(
        self,
        kind: str,
        color: Optional[Union[str, int]] = None,
        fillColor: Optional[Union[str, int]] = None,
        height: Optional[int] = None,
        text: Optional[str] = None,
        textColor: Optional[Union[str, int]] = None,
        url: Optional[str] = None,
        width: Optional[int] = None,
    ) -> Hover:
        """Generate an instance of :class:`.Hover`.

        .. note:: You can use hover states that do not correspond with the
            given button type, such as an ``image`` hover state for a ``text``
            button.

        :param kind: The type of hover state (``image`` or ``text``)
        :param text: The hover state text.
        :param url: The link to an uploaded image obtained from
            :meth:`.upload_image`. Can only be used on ``image`` hover states.
        :param color: The color of the hover state. Should either be given as a
            7-character RGB code (``"#FFFFFF"``) or the integer representation
            (``0xFFFFFF``).
        :param fillColor: The background color of the hover state. Should
            either be given as a 7-character RGB code (``"#FFFFFF"``) or the
            integer representation (``0xFFFFFF``).
        :param height: The height of the image, if the hover state is an image
            hover state.
        :param textColor: The color of the hover state text. Should either be
            given as a 7-character RGB code (``"#FFFFFF"``) or the integer
            representation (``0xFFFFFF``).
        :param width: The width of the image, if the hover state is an image
            hover state.
        :returns: An instance of :class:`.Hover`.
        """
        data = {"kind": kind}
        for name, value in {
            "color": color,
            "fillColor": fillColor,
            "height": height,
            "text": text,
            "textColor": textColor,
            "url": url,
            "width": width,
        }.items():
            if value is not None:
                data[name] = value
        return Hover(self._reddit, data)

    def generate_image(
        self, url: str, width: int, height: int, linkUrl: str = ""
    ) -> Image:
        """Generate an instance of :class:`.Image`.

        This method should be used along with :meth:`.add_image_widget`.

        :param url: The url for the image, as returned from
            :meth:`.upload_image`.
        :param width: The width of the image.
        :param height: The height of the image.
        :param linkUrl: The URL that clicking on the image will go to.
            Optional.
        :returns: An instance of :class:`.Image`.
        """
        return Image(
            self._reddit,
            {"url": url, "width": width, "height": height, "linkUrl": linkUrl},
        )

    def generate_image_data(
        self, url: str, width: int, height: int, name: int
    ) -> ImageData:
        """Generate an instance of :class:`.ImageData`.

        This method should be used along with :meth:`.add_custom_widget`.

        :param url: The url for the image, as returned from
            :meth:`.upload_image`.
        :param width: The width of the image.
        :param height: The height of the image.
        :param name: The name of the image.
        :returns: An instance of :class:`.ImageData`.
        """
        return ImageData(
            self._reddit,
            {"url": url, "width": width, "height": height, "name": name},
        )

    def generate_menu_link(self, text: str, url: str) -> MenuLink:
        """Generate an instance of :class:`.MenuLink`.

        This method should be used along with :meth:`.add_menu` and
        :meth:`.generate_submenu`.

        :param text: The text of the menu link.
        :param url: The url that the menu link points to.
        :returns: An instance of :class:`.MenuLink`.

        Example usage:

        .. code-block:: python

            menu_link = widget_moderation.generate_menu_link("Reddit Homepage",
                "https://www.reddit.com")
        """
        return MenuLink(self._reddit, {"text": text, "url": url})

    def generate_styles(
        self, backgroundColor: Union[str, int], headerColor: Union[str, int]
    ) -> Styles:
        """Generate an instance of :class:`.Styles`.

        :param backgroundColor: The background color of a widget. Should either
            be given as a 7-character RGB code (``"#FFFFFF"``) or the integer
            representation (``0xFFFFFF``).
        :param headerColor: The color of the widget header. Should either be
            given as a 7-character RGB code (``"#FFFFFF"``) or the integer
            representation (``0xFFFFFF``).
        :returns: An instance of :class:`.Styles`.

        .. note:: Porting code is relatively simple using the ``**`` dictionary
            keyword argument. For example, given the dict:

            .. code-block:: python

                styles = {
                    "backgroundColor": "#FFFF66","headerColor": "#3333EE"
                }

            By adding ``**``, it can easily be converted to an instance of
            :class:`.Styles`, like so:

            .. code-block:: python

                widget_mod = reddit.subreddit("test").widgets.mod
                styles = widget_mod.generate_styles(**{
                    "backgroundColor": "#FFFF66","headerColor": "#3333EE"
                })

        """
        return Styles(
            self._reddit,
            {"backgroundColor": backgroundColor, "headerColor": headerColor},
        )

    def generate_submenu(
        self, children: List[Union[MenuLink, Dict[str, str]]], text: str
    ) -> Submenu:
        """Generate an instance of :class:`.Submenu`.

        :param children: A list of instances of :class:`.MenuLink`.
        :param text: The text for the submenu.
        :returns: An instance of :class:`.Submenu`.

        Example usage:

        .. code-block:: python

            submenu = widget_moderation.generate_submenu(
                [
                    widget_moderation.generate_menu_link(
                        "PRAW", "https://praw.readthedocs.io/"
                    ),
                    widget_moderation.generate_menu_link(
                        "requests", "https://requests.readthedocs.io/"
                    ),
                ],
                "Python packages",
            )
        """
        return Submenu(self._reddit, {"children": children, "text": text})

    def reorder(
        self, new_order: List[Union[str, "Widget"]], section: str = "sidebar"
    ):
        """Reorder the widgets.

        :param new_order: A list of widgets. Represented as a ``list`` that
            contains ``Widget`` objects, or widget IDs as strings. These types
            may be mixed.
        :param section: The section to reorder. (default: ``"sidebar"``)

        Example usage:

        .. code-block:: python

           widgets = reddit.subreddit("mysub").widgets
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

    def upload_image(self, file_path: str) -> str:
        """Upload an image to Reddit and get the URL.

        :param file_path: The path to the local file.
        :returns: The URL of the uploaded image as a ``str``.

        This method is used to upload images for widgets. For example,
        it can be used in conjunction with :meth:`.add_image_widget`,
        :meth:`.add_custom_widget`, and :meth:`.add_button_widget`.

        Example usage:

        .. code-block:: python

           my_sub = reddit.subreddit("my_sub")
           image_url = my_sub.widgets.mod.upload_image("/path/to/image.jpg")
           images = [{"width": 300, "height": 300,
                      "url": image_url, "linkUrl": ''}]
           styles = {"backgroundColor": "#FFFF66", "headerColor": "#3333EE"}
           my_sub.widgets.mod.add_image_widget("My cool pictures", images,
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


class Widget(WidgetBase):
    """Base class to represent a Widget."""

    @cachedproperty
    def mod(self) -> "WidgetModeration":
        """Get an instance of :class:`.WidgetModeration` for this widget.

        .. note::
           Using any of the methods of :class:`.WidgetModeration` will likely
           make outdated the data in the :class:`.SubredditWidgets` that this
           widget belongs to. To remedy this, call
           :meth:`~.SubredditWidgets.refresh`.
        """
        return WidgetModeration(self, self.subreddit, self._reddit)

    def __eq__(self: _T, other: _T) -> bool:
        """Check equality against another object."""
        if isinstance(other, Widget):
            return self.id.lower() == other.id.lower()
        return str(other).lower() == self.id.lower()

    def __repr__(self) -> str:
        """Return a string representation of the Widget."""
        return "<{} widget>".format(self.__class__.__name__)

    def __init__(self, reddit: "Reddit", _data: Optional[Dict[str, Any]]):
        """Initialize an instance of the class."""
        self.subreddit = ""  # in case it isn't in _data
        self.id = ""  # in case it isn't in _data
        super().__init__(reddit, _data=_data)
        # Deal with cases where subclass's CHILD_ATTRIBUTE values are missing
        if hasattr(self, "CHILD_ATTRIBUTE"):
            if getattr(self, self.CHILD_ATTRIBUTE, object) == object:
                setattr(self, self.CHILD_ATTRIBUTE, [])


class ButtonWidget(BaseList, Widget):
    r"""Class to represent a widget containing one or more buttons.

    Find an existing one:

    .. code-block:: python

       button_widget = None
       widgets = reddit.subreddit("redditdev").widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.ButtonWidget):
               button_widget = widget
               break

       for button in button_widget:
           print(button.text, button.url)

    Create one (requires proper moderator permissions):

    .. code-block:: python

       widgets = reddit.subreddit("redditdev").widgets
       buttons = [
           {
               "kind": "text",
               "text": "View source",
               "url": 'https://github.com/praw-dev/praw',
               "color": "#FF0000",
               "textColor": "#00FF00",
               "fillColor": "#0000FF",
               "hoverState": {
                   "kind": "text",
                   "text": "ecruos weiV",
                   "color": "#000000",
                   "textColor": "#FFFFFF",
                   "fillColor": "#0000FF"
               }
           },
           {
               "kind": "text",
               "text": "View documentation",
               "url": 'https://praw.readthedocs.io',
               "color": "#FFFFFF",
               "textColor": "#FFFF00",
               "fillColor": "#0000FF"
           },
       ]
       styles = {"backgroundColor": "#FFFF66", "headerColor": "#3333EE"}
       button_widget = widgets.mod.add_button_widget(
           "Things to click", "Click some of these *cool* links!",
           buttons, styles)

    For more information on creation, see :meth:`.add_button_widget`.

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {"backgroundColor": "#FFFFFF", "headerColor": "#FF9900"}
       button_widget = button_widget.mod.update(shortName="My fav buttons",
                                                styles=new_styles)

    Delete one (requires proper moderator permissions):

    .. code-block:: python

       button_widget.mod.delete()

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``buttons``             A ``list`` of :class:`.Button`\ s. These can also
                            be accessed just by iterating over the
                            :class:`.ButtonWidget` (e.g. ``for button in
                            button_widget``).
    ``description``         The description, in Markdown.
    ``description_html``    The description, in HTML.
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``"button"``).
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``"backgroundColor"`` and
                            ``"headerColor"``.
    ``subreddit``           The :class:`.Subreddit` the button widget belongs
                            to.
    ======================= ===================================================
    """

    CHILD_ATTRIBUTE = "buttons"


class Calendar(Widget):
    r"""Class to represent a calendar widget.

    Find an existing one:

    .. code-block:: python

       calendar = None
       widgets = reddit.subreddit("redditdev").widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.Calendar):
               calendar = widget
               break

       print(calendar.googleCalendarId)

    Create one (requires proper moderator permissions):

    .. code-block:: python

       widgets = reddit.subreddit("redditdev").widgets
       styles = {"backgroundColor": "#FFFF66", "headerColor": "#3333EE"}
       config = {"numEvents": 10,
                 "showDate": True,
                 "showDescription": False,
                 "showLocation": False,
                 "showTime": True,
                 "showTitle": True}
       cal_id = "y6nm89jy427drk8l71w75w9wjn@group.calendar.google.com"
       calendar = widgets.mod.add_calendar(
           "Upcoming Events", cal_id, True, config, styles)

    For more information on creation, see :meth:`.add_calendar`.

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {"backgroundColor": "#FFFFFF", "headerColor": "#FF9900"}
       calendar = calendar.mod.update(shortName="My fav events",
                                      styles=new_styles)

    Delete one (requires proper moderator permissions):

    .. code-block:: python

       calendar.mod.delete()

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``configuration``       A ``dict`` describing the calendar configuration.
    ``data``                A ``list`` of ``dict``\ s that represent events.
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``"calendar"``).
    ``requiresSync``        A ``bool``.
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``"backgroundColor"`` and
                            ``"headerColor"``.
    ``subreddit``           The :class:`.Subreddit` the calendar widget belongs
                            to.
    ======================= ===================================================
    """

    def __setattr__(
        self, name: str, value: Union[str, Dict[str, Union[int, bool]]]
    ):
        """Objectify ``configuration``."""
        if name == "configuration" and self._reddit.config.widgets_beta:
            value = CalendarConfiguration(self._reddit, value)
        super().__setattr__(name, value)


class CommunityList(BaseList, Widget):
    r"""Class to represent a Related Communities widget.

    Find an existing one:

    .. code-block:: python

       community_list = None
       widgets = reddit.subreddit("redditdev").widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.CommunityList):
               community_list = widget
               break

       print(community_list)

    Create one (requires proper moderator permissions):

    .. code-block:: python

       widgets = reddit.subreddit("redditdev").widgets
       styles = {"backgroundColor": "#FFFF66", "headerColor": "#3333EE"}
       subreddits = ["learnpython", reddit.subreddit("announcements")]
       community_list = widgets.mod.add_community_list("Related subreddits",
                                                       subreddits, styles,
                                                       "description")

    For more information on creation, see :meth:`.add_community_list`.

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {"backgroundColor": "#FFFFFF", "headerColor": "#FF9900"}
       community_list = community_list.mod.update(shortName="My fav subs",
                                                  styles=new_styles)

    Delete one (requires proper moderator permissions):

    .. code-block:: python

       community_list.mod.delete()

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``data``                A ``list`` of :class:`.Subreddit`\ s. These can
                            also be iterated over by iterating over the
                            :class:`.CommunityList` (e.g. ``for sub in
                            community_list``).
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``"community-list"``).
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``"backgroundColor"`` and
                            ``"headerColor"``.
    ``subreddit``           The :class:`.Subreddit` the button widget belongs
                            to.
    ======================= ===================================================
    """

    CHILD_ATTRIBUTE = "data"


class CustomWidget(Widget):
    """Class to represent a custom widget.

    Find an existing one:

    .. code-block:: python

       custom = None
       widgets = reddit.subreddit("redditdev").widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.CustomWidget):
               custom = widget
               break

       print(custom.text)
       print(custom.css)

    Create one (requires proper moderator permissions):

    .. code-block:: python

       widgets = reddit.subreddit("redditdev").widgets
       styles = {"backgroundColor": "#FFFF66", "headerColor": "#3333EE"}
       custom = widgets.mod.add_custom_widget(
           "My custom widget", "# Hello world!", "/**/", 200, [], styles)

    For more information on creation, see :meth:`.add_custom_widget`.

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {"backgroundColor": "#FFFFFF", "headerColor": "#FF9900"}
       custom = custom.mod.update(shortName="My fav customization",
                                  styles=new_styles)

    Delete one (requires proper moderator permissions):

    .. code-block:: python

       custom.mod.delete()

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``css``                 The CSS of the widget, as a ``str``.
    ``height``              The height of the widget, as an ``int``.
    ``id``                  The widget ID.
    ``imageData``           A ``list`` of :class:`.ImageData` that belong to
                            the widget.
    ``kind``                The widget kind (always ``"custom"``).
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``"backgroundColor"`` and
                            ``"headerColor"``.
    ``stylesheetUrl``       A link to the widget's stylesheet.
    ``subreddit``           The :class:`.Subreddit` the button widget belongs
                            to.
    ``text``                The text contents, as Markdown.
    ``textHtml``            The text contents, as HTML.
    ======================= ===================================================
    """

    def __setattr__(
        self,
        name: str,
        value: Union[str, Dict[str, Union[str, Dict[str, Union[str, int]]]]],
    ):
        """Objectify ``imageData``."""
        if name == "imageData":
            value = [ImageData(self._reddit, item) for item in value]
        super().__setattr__(name, value)


class IDCard(Widget):
    """Class to represent an ID card widget.

    .. code-block:: python

       widgets = reddit.subreddit("redditdev").widgets
       id_card = widgets.id_card
       print(id_card.subscribersText)

    Update one (requires proper moderator permissions):

    .. code-block:: python

       widgets.id_card.mod.update(currentlyViewingText="Bots")

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    =========================== ===============================================
    Attribute                   Description
    =========================== ===============================================
    ``currentlyViewingCount``   The number of Redditors viewing the subreddit.
    ``currentlyViewingText``    The text displayed next to the view count. For
                                example, "users online".
    ``description``             The subreddit description.
    ``id``                      The widget ID.
    ``kind``                    The widget kind (always ``"id-card"``).
    ``shortName``               The short name of the widget.
    ``styles``                  A ``dict`` with the keys ``"backgroundColor"``
                                and ``"headerColor"``.
    ``subreddit``               The :class:`.Subreddit` the button widget
                                belongs to.
    ``subscribersCount``        The number of subscribers to the subreddit.
    ``subscribersText``         The text displayed next to the subscriber
                                count. For example, "users subscribed".
    =========================== ===============================================
    """


class ImageWidget(BaseList, Widget):
    r"""Class to represent an image widget.

    Find an existing one:

    .. code-block:: python

       image_widget = None
       widgets = reddit.subreddit("redditdev").widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.ImageWidget):
               image_widget = widget
               break

       for image in image_widget:
           print(image.url)

    Create one (requires proper moderator permissions):

    .. code-block:: python

       widgets = reddit.subreddit("redditdev").widgets
       image_paths = ["/path/to/image1.jpg", "/path/to/image2.png"]
       image_dicts = [{"width": 600, "height": 450, "linkUrl": '',
                       "url": widgets.mod.upload_image(img_path)}
                      for img_path in image_paths]
       styles = {"backgroundColor": "#FFFF66", "headerColor": "#3333EE"}
       image_widget = widgets.mod.add_image_widget("My cool pictures",
                                                   image_dicts, styles)

    For more information on creation, see :meth:`.add_image_widget`.

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {"backgroundColor": "#FFFFFF", "headerColor": "#FF9900"}
       image_widget = image_widget.mod.update(shortName="My fav images",
                                              styles=new_styles)

    Delete one (requires proper moderator permissions):

    .. code-block:: python

       image_widget.mod.delete()

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``data``                A list of the :class:`.Image`\ s in this widget.
                            Can be iterated over by iterating over the
                            :class:`.ImageWidget` (e.g. ``for img in
                            image_widget``).
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``"image"``).
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``"backgroundColor"`` and
                            ``"headerColor"``.
    ``subreddit``           The :class:`.Subreddit` the button widget belongs
                            to.
    ======================= ===================================================
    """

    CHILD_ATTRIBUTE = "data"


class Menu(BaseList, Widget):
    r"""Class to represent the top menu widget of a subreddit.

    Menus can generally be found as the first item in a subreddit's top bar.

    .. code-block:: python

       topbar = reddit.subreddit("redditdev").widgets.topbar
       if len(topbar) > 0:
           probably_menu = topbar[0]
           assert isinstance(probably_menu, praw.models.Menu)
           for item in probably_menu:
               if isinstance(item, praw.models.Submenu):
                   print(item.text)
                   for child in item:
                       print("\t", child.text, child.url)
               else:  # MenuLink
                   print(item.text, item.url)

    Create one (requires proper moderator permissions):

    .. code-block:: python

       widgets = reddit.subreddit("redditdev").widgets
       menu_contents = [
           {"text": "My homepage", "url": 'https://example.com'},
           {"text": "Python packages",
            "children": [
                {"text": "PRAW", "url": 'https://praw.readthedocs.io/'},
                {"text": "requests", "url": 'http://python-requests.org'}
            ]},
           {"text": "Reddit homepage", "url": 'https://reddit.com'}
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
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``data``                A list of the :class:`.MenuLink`\ s and
                            :class:`.Submenu`\ s in this widget.
                            Can be iterated over by iterating over the
                            :class:`.Menu` (e.g. ``for item in menu``).
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``"menu"``).
    ``subreddit``           The :class:`.Subreddit` the button widget belongs
                            to.
    ======================= ===================================================

    """

    CHILD_ATTRIBUTE = "data"


class ModeratorsWidget(BaseList, Widget):
    r"""Class to represent a moderators widget.

    .. code-block:: python

       widgets = reddit.subreddit("redditdev").widgets
       print(widgets.moderators_widget)

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {"backgroundColor": "#FFFFFF", "headerColor": "#FF9900"}
       widgets.moderators_widget.mod.update(styles=new_styles)

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``"moderators"``).
    ``mods``                A list of the :class:`.Redditor`\ s that moderate
                            the subreddit. Can be iterated over by iterating
                            over the :class:`.ModeratorsWidget` (e.g. ``for
                            mod in widgets.moderators_widget``).
    ``styles``              A ``dict`` with the keys ``"backgroundColor"``
                            and ``"headerColor"``.
    ``subreddit``           The :class:`.Subreddit` the button widget
                            belongs to.
    ``totalMods``           The total number of moderators in the subreddit.
    ======================= ===================================================
    """

    CHILD_ATTRIBUTE = "mods"


class PostFlairWidget(BaseList, Widget):
    r"""Class to represent a post flair widget.

    Find an existing one:

    .. code-block:: python

       post_flair_widget = None
       widgets = reddit.subreddit("redditdev").widgets
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.PostFlairWidget):
               post_flair_widget = widget
               break

       for flair in post_flair_widget:
           print(flair)
           print(post_flair_widget.templates[flair])

    Create one (requires proper moderator permissions):

    .. code-block:: python

       subreddit = reddit.subreddit("redditdev")
       widgets = subreddit.widgets
       flairs = [f["id"] for f in subreddit.flair.link_templates]
       styles = {"backgroundColor": "#FFFF66", "headerColor": "#3333EE"}
       post_flair = widgets.mod.add_post_flair_widget("Some flairs", "list",
                                                      flairs, styles)

    For more information on creation, see :meth:`.add_post_flair_widget`.

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {"backgroundColor": "#FFFFFF", "headerColor": "#FF9900"}
       post_flair = post_flair.mod.update(shortName="My fav flairs",
                                          styles=new_styles)

    Delete one (requires proper moderator permissions):

    .. code-block:: python

       post_flair.mod.delete()

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``display``             The display style of the widget, either ``"cloud"``
                            or ``"list"``.
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``"post-flair"``).
    ``order``               A list of the flair IDs in this widget.
                            Can be iterated over by iterating over the
                            :class:`.PostFlairWidget` (e.g. ``for flair_id in
                            post_flair``).
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``"backgroundColor"`` and
                            ``"headerColor"``.
    ``subreddit``           The :class:`.Subreddit` the button widget belongs
                            to.
    ``templates``           A ``dict`` that maps flair IDs to ``dict``\ s that
                            describe flairs.
    ======================= ===================================================
    """

    CHILD_ATTRIBUTE = "order"


class RulesWidget(BaseList, Widget):
    """Class to represent a rules widget.

    .. code-block:: python

       widgets = reddit.subreddit("redditdev").widgets
       rules_widget = None
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.RulesWidget):
               rules_widget = widget
               break
       from pprint import pprint; pprint(rules_widget.data)

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {"backgroundColor": "#FFFFFF", "headerColor": "#FF9900"}
       rules_widget.mod.update(display="compact", shortName="The LAWS",
                               styles=new_styles)

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``data``                A list of the subreddit rules.
                            Can be iterated over by iterating over the
                            :class:`.RulesWidget` (e.g. ``for rule in
                            rules_widget``).
    ``display``             The display style of the widget, either ``"full"``
                            or ``"compact"``.
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``"subreddit-rules"``).
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``"backgroundColor"``
                            and ``"headerColor"``.
    ``subreddit``           The :class:`.Subreddit` the button widget
                            belongs to.
    ======================= ===================================================
    """

    CHILD_ATTRIBUTE = "data"


class TextArea(Widget):
    """Class to represent a text area widget.

    Find a text area in a subreddit:

    .. code-block:: python

       widgets = reddit.subreddit("redditdev").widgets
       text_area = None
       for widget in widgets.sidebar:
           if isinstance(widget, praw.models.TextArea):
               text_area = widget
               break
       print(text_area.text)

    Create one (requires proper moderator permissions):

    .. code-block:: python

       widgets = reddit.subreddit("redditdev").widgets
       styles = {"backgroundColor": "#FFFF66", "headerColor": "#3333EE"}
       text_area = widgets.mod.add_text_area("My cool title",
                                             "*Hello* **world**!",
                                             styles)

    For more information on creation, see :meth:`.add_text_area`.

    Update one (requires proper moderator permissions):

    .. code-block:: python

       new_styles = {"backgroundColor": "#FFFFFF", "headerColor": "#FF9900"}
       text_area = text_area.mod.update(shortName="My fav text",
                                        styles=new_styles)

    Delete one (requires proper moderator permissions):

    .. code-block:: python

       text_area.mod.delete()

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``id``                  The widget ID.
    ``kind``                The widget kind (always ``"textarea"``).
    ``shortName``           The short name of the widget.
    ``styles``              A ``dict`` with the keys ``"backgroundColor"`` and
                            ``"headerColor"``.
    ``subreddit``           The :class:`.Subreddit` the button widget belongs
                            to.
    ``text``                The widget's text, as Markdown.
    ``textHtml``            The widget's text, as HTML.
    ======================= ===================================================
    """


class WidgetEncoder(JSONEncoder):
    """Class to encode widget-related objects."""

    def default(
        self, o: Union["Subreddit", PRAWBase, Any]
    ) -> Union[str, Dict[str, Any]]:  # pylint: disable=E0202
        """Serialize ``PRAWBase`` objects."""
        if isinstance(o, self._subreddit_class):
            return str(o)
        elif isinstance(o, PRAWBase):
            return SubredditWidgetsModeration._convert_color_to_RGB(
                {
                    key: val
                    for key, val in vars(o).items()
                    if not key.startswith("_")
                }
            )
        return super().default(o)


class WidgetModeration:
    """Class for moderating a particular widget.

    Example usage:

    .. code-block:: python

       widget = reddit.subreddit("my_sub").widgets.sidebar[0]
       widget.mod.update(shortName="My new title")
       widget.mod.delete()
    """

    def __init__(
        self, widget: Widget, subreddit: "Subreddit", reddit: "Reddit"
    ):
        """Initialize the widget moderation object."""
        self.widget = widget
        self._reddit = reddit
        self._subreddit = subreddit

    def delete(self):
        """Delete the widget.

        Example usage:

        .. code-block:: python

           widget.mod.delete()
        """
        path = API_PATH["widget_modify"].format(
            widget_id=self.widget.id, subreddit=self._subreddit
        )
        self._reddit.delete(path)

    def update(self, **kwargs: Any) -> Widget:
        """Update the widget. Returns the updated widget.

        Parameters differ based on the type of widget. See
        `Reddit documentation
        <https://www.reddit.com/dev/api#PUT_api_widget_{widget_id}>`_ or the
        document of the particular type of widget.
        For example, update a text widget like so:

        .. code-block:: python

           text_widget.mod.update(shortName="New text area", text="Hello!")

        .. note::

           Most parameters follow the ``lowerCamelCase`` convention. When in
           doubt, check the Reddit documentation linked above.
        """
        path = API_PATH["widget_modify"].format(
            widget_id=self.widget.id, subreddit=self._subreddit
        )
        payload = {
            key: value
            for key, value in vars(self.widget).items()
            if not key.startswith("_")
        }
        del payload["subreddit"]  # not JSON serializable
        del payload["mod"]
        payload.update(kwargs)
        widget = self._reddit.put(
            path, data={"json": dumps(payload, cls=WidgetEncoder)}
        )
        widget.subreddit = self._subreddit
        return widget
