from json import dumps
from unittest import mock

from pytest import raises

from praw.models import (
    Button,
    CalendarConfiguration,
    Hover,
    Image,
    ImageData,
    MenuLink,
    Styles,
    Submenu,
    SubredditWidgets,
    SubredditWidgetsModeration,
    Widget,
    WidgetModeration,
)
from praw.models.base import PRAWBase
from praw.models.reddit.widgets import WidgetEncoder

from ... import UnitTest


class TestWidgetEncoder(UnitTest):
    def test_bad_encode(self):
        data = [
            1,
            "two",
            SubredditWidgetsModeration(
                self.reddit.subreddit("subreddit"), self.reddit
            ),
        ]
        with raises(TypeError):
            dumps(data, cls=WidgetEncoder)  # should throw TypeError

    def test_good_encode(self):
        data = [
            1,
            "two",
            PRAWBase(self.reddit, _data={"_secret": "no", "3": 3}),
            self.reddit.subreddit("four"),
        ]
        assert '[1, "two", {"3": 3}, "four"]' == dumps(data, cls=WidgetEncoder)


class TestWidgets(UnitTest):
    def test_subredditwidgets_mod(self):
        sw = SubredditWidgets(self.reddit.subreddit("fake_subreddit"))
        assert isinstance(sw.mod, SubredditWidgetsModeration)

    def test_widget_mod(self):
        w = Widget(self.reddit, {})
        assert isinstance(w.mod, WidgetModeration)
        assert w.mod.widget == w


class TestSubredditWidgetsModeration(UnitTest):
    @mock.patch(
        "praw.models.reddit.widgets.SubredditWidgetsModeration.upload_image",
        side_effect=lambda value: value,
    )
    def test_generate_buttons(self, _):
        widget_mod = self.reddit.subreddit("test").widgets.mod
        text_hover = widget_mod.generate_hover(
            "text",
            color=0xFF0000,
            fillColor=0x000000,
            text="Don't click me",
            textColor=0xFFFFFF,
            url="https://www.reddit.com",
        )
        text_button = widget_mod.generate_button(
            "text",
            "Click me!",
            "https://www.google.com",
            color=0x00FF00,
            fillColor=0xFFFFFF,
            hoverState=text_hover,
            textColor=0x000000,
        )
        image = widget_mod.upload_image("image.png")
        image_button = widget_mod.generate_button(
            "image",
            "Click me!",
            image,
            height=200,
            linkUrl="https://www.google.com",
            width=200,
        )
        assert isinstance(text_button, Button)
        assert text_button.kind == "text"
        assert text_button.color == 0x00FF00
        assert text_button.text == "Click me!"
        assert text_button.url == "https://www.google.com"
        assert text_button.fillColor == 0xFFFFFF
        assert text_button.textColor == 0x000000
        assert text_button.hoverState == text_hover
        assert isinstance(image_button, Button)
        assert image_button.kind == "image"
        assert image_button.text == "Click me!"
        assert image_button.url == image
        assert image_button.height == 200
        assert image_button.linkUrl == "https://www.google.com"
        assert image_button.width == 200

    def test_generate_calendar_configuration(self):
        widget_moderation = self.reddit.subreddit("mysub").widgets.mod
        config = widget_moderation.generate_calendar_configuration(
            numEvents=10,
            showDate=True,
            showDescription=False,
            showLocation=False,
            showTime=True,
            showTitle=True,
        )
        assert isinstance(config, CalendarConfiguration)
        assert config.numEvents == 10
        assert config.showDate
        assert not config.showDescription
        assert not config.showLocation
        assert config.showTime
        assert config.showTitle

    @mock.patch(
        "praw.models.reddit.widgets.SubredditWidgetsModeration.upload_image",
        side_effect=lambda value: value,
    )
    def test_generate_hover(self, _):
        widget_mod = self.reddit.subreddit("test").widgets.mod
        text_hover = widget_mod.generate_hover(
            "text",
            color=0xFF0000,
            fillColor=0x000000,
            text="Don't click me",
            textColor=0xFFFFFF,
            url="https://www.reddit.com",
        )
        image = widget_mod.upload_image("image.png")
        image_hover = widget_mod.generate_hover(
            "image",
            linkUrl="https://www.reddit.com",
            height=400,
            text="Don't click me",
            url=image,
            width=200,
        )
        assert isinstance(text_hover, Hover)
        assert text_hover.kind == "text"
        assert text_hover.color == 0xFF0000
        assert text_hover.fillColor == 0x000000
        assert text_hover.text == "Don't click me"
        assert text_hover.textColor == 0xFFFFFF
        assert text_hover.url == "https://www.reddit.com"
        assert isinstance(image_hover, Hover)
        assert image_hover.kind == "image"
        assert image_hover.linkUrl == "https://www.reddit.com"
        assert image_hover.height == 400
        assert image_hover.text == "Don't click me"
        assert image_hover.url == image
        assert image_hover.width == 200

    @mock.patch(
        "praw.models.reddit.widgets.SubredditWidgetsModeration.upload_image",
        side_effect=lambda value: value,
    )
    def test_generate_image(self, _):
        widget_moderation = self.reddit.subreddit("mysub").widgets.mod
        image_url = widget_moderation.upload_image("/path/to/image.png")
        image = widget_moderation.generate_image(image_url, 600, 450)
        assert isinstance(image, Image)
        assert image.url == image_url
        assert image.width == 600
        assert image.height == 450
        assert image.linkUrl == ""
        image2 = widget_moderation.generate_image(
            image_url, 600, 450, linkUrl="https://www.google.com"
        )
        assert image2.url == image_url
        assert image2.width == 600
        assert image2.height == 450
        assert image2.linkUrl == "https://www.google.com"

    @mock.patch(
        "praw.models.reddit.widgets.SubredditWidgetsModeration.upload_image",
        side_effect=lambda value: value,
    )
    def test_generate_image_data(self, _):
        widget_moderation = self.reddit.subreddit("mysub").widgets.mod
        image_url = widget_moderation.upload_image("/path/to/image.png")
        image_data = widget_moderation.generate_image_data(
            image_url, 600, 450, "Test"
        )
        assert isinstance(image_data, ImageData)
        assert image_data.url == image_url
        assert image_data.width == 600
        assert image_data.height == 450
        assert image_data.name == "Test"

    def test_generate_menu_link(self):
        widget_moderation = self.reddit.subreddit("mysub").widgets.mod
        menu_link = widget_moderation.generate_menu_link(
            "Reddit Homepage", "https://www.reddit.com"
        )
        assert isinstance(menu_link, MenuLink)
        assert menu_link.text == "Reddit Homepage"
        assert menu_link.url == "https://www.reddit.com"

    def test_generate_styles(self):
        widget_moderation = self.reddit.subreddit("test").widgets.mod
        styles = widget_moderation.generate_styles(
            backgroundColor="#FFFF66", headerColor="#3333EE"
        )
        assert isinstance(styles, Styles)
        assert styles.backgroundColor == "#FFFF66"
        assert styles.headerColor == "#3333EE"

    def test_generate_submenu(self):
        widget_moderation = self.reddit.subreddit("test").widgets.mod
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
        assert isinstance(submenu, Submenu)
        assert submenu.text == "Python packages"
        for item in submenu.children:
            assert isinstance(item, MenuLink)
