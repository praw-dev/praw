import sys
from os.path import abspath, dirname, join
from unittest import mock

import pytest

from praw.models import (
    Button,
    ButtonWidget,
    Calendar,
    CommunityList,
    CustomWidget,
    IDCard,
    Image,
    ImageData,
    ImageWidget,
    Menu,
    MenuLink,
    ModeratorsWidget,
    PostFlairWidget,
    Redditor,
    RulesWidget,
    Submenu,
    Subreddit,
    TextArea,
    Widget,
)

from ... import IntegrationTest

if sys.version_info.major > 2:
    basestring = str  # pylint: disable=invalid-name


class TestButtonWidget(IntegrationTest):
    @staticmethod
    def image_path(name):
        test_dir = abspath(dirname(sys.modules[__name__].__file__))
        return join(test_dir, "..", "..", "files", name)

    def test_button_widget(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            button_widget = None
            for widget in widgets.sidebar:
                if isinstance(widget, ButtonWidget):
                    button_widget = widget
                    break
            assert isinstance(button_widget, ButtonWidget)
            assert len(button_widget) >= 1
            assert all(isinstance(button, Button) for button in button_widget.buttons)
            assert button_widget == button_widget
            assert button_widget.id == button_widget
            assert button_widget in widgets.sidebar

            assert button_widget[0].text
            assert button_widget.shortName
            assert hasattr(button_widget, "description")

            assert subreddit == button_widget.subreddit

    @mock.patch("time.sleep", return_value=None)
    def test_create_and_update_and_delete(self, _):
        self.reddit.read_only = False

        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets

        with self.use_cassette():
            styles = {"headerColor": "#123456", "backgroundColor": "#bb0e00"}
            my_image = widgets.mod.upload_image(self.image_path("test.png"))
            buttons = [
                {
                    "kind": "text",
                    "text": "View source",
                    "url": "https://github.com/praw-dev/praw",
                    "color": "#FF0000",
                    "textColor": "#00FF00",
                    "fillColor": "#0000FF",
                    "hoverState": {
                        "kind": "text",
                        "text": "VIEW SOURCE!",
                        "color": "#FFFFFF",
                        "textColor": "#000000",
                        "fillColor": "#0000FF",
                    },
                },
                {
                    "kind": "image",
                    "text": "View documentation",
                    "linkUrl": "https://praw.readthedocs.io",
                    "url": my_image,
                    "height": 200,
                    "width": 200,
                    "hoverState": {
                        "kind": "image",
                        "url": my_image,
                        "height": 200,
                        "width": 200,
                    },
                },
                {
                    "kind": "text",
                    "text": "/r/redditdev",
                    "url": "https://reddit.com/r/redditdev",
                    "color": "#000000",
                    "textColor": "#FF00FF",
                    "fillColor": "#005500",
                },
            ]
            widget = widgets.mod.add_button_widget(
                "Things to click",
                "Click some of these *cool* links!",
                buttons,
                styles,
            )

            assert isinstance(widget, ButtonWidget)
            assert len(widget) == 3
            assert all(isinstance(item, Button) for item in widget)
            assert widget.shortName == "Things to click"
            assert widget.description == "Click some of these *cool* links!"
            assert widget.styles == styles

            assert widget[0].text == "View source"
            assert widget[0].url == "https://github.com/praw-dev/praw"
            assert widget[2].text == "/r/redditdev"
            assert widget[2].url == "https://reddit.com/r/redditdev"

            assert widget[1].text == "View documentation"
            assert widget[1].linkUrl == "https://praw.readthedocs.io"
            assert widget[1].hoverState["kind"] == "image"
            assert widget[1].hoverState["height"] == 200

            widgets.refresh()  # the links are initially invalid
            for new_widget in widgets.sidebar:
                if new_widget == widget:
                    widget = new_widget
                    break

            widget = widget.mod.update(shortName="New short name")

            assert isinstance(widget, ButtonWidget)
            assert len(widget) == 3
            assert all(isinstance(item, Button) for item in widget)
            assert widget.shortName == "New short name"
            assert widget.description == "Click some of these *cool* links!"
            assert widget.styles == styles

            assert widget[0].text == "View source"
            assert widget[0].url == "https://github.com/praw-dev/praw"
            assert widget[2].text == "/r/redditdev"
            assert widget[2].url == "https://reddit.com/r/redditdev"

            assert widget[1].text == "View documentation"
            assert widget[1].linkUrl == "https://praw.readthedocs.io"
            assert widget[1].hoverState["kind"] == "image"
            assert widget[1].hoverState["height"] == 200

            buttons.reverse()
            widget = widget.mod.update(buttons=buttons)

            assert isinstance(widget, ButtonWidget)
            assert len(widget) == 3
            assert all(isinstance(item, Button) for item in widget)
            assert widget.shortName == "New short name"
            assert widget.description == "Click some of these *cool* links!"
            assert widget.styles == styles

            assert widget[0].text == "/r/redditdev"
            assert widget[0].url == "https://reddit.com/r/redditdev"
            assert widget[2].text == "View source"
            assert widget[2].url == "https://github.com/praw-dev/praw"

            assert widget[1].text == "View documentation"
            assert widget[1].linkUrl == "https://praw.readthedocs.io"
            assert widget[1].hoverState["kind"] == "image"
            assert widget[1].hoverState["height"] == 200

            widget.mod.delete()


class TestCalendar(IntegrationTest):
    def test_calendar(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            calendar = None
            for widget in widgets.sidebar:
                if isinstance(widget, Calendar):
                    calendar = widget
                    break
            assert isinstance(calendar, Calendar)
            assert calendar == calendar
            assert calendar.id == calendar
            assert calendar in widgets.sidebar

            assert isinstance(calendar.configuration, dict)
            assert hasattr(calendar, "requiresSync")

            assert subreddit == calendar.subreddit

    @mock.patch("time.sleep", return_value=None)
    def test_create_and_update_and_delete(self, _):
        self.reddit.read_only = False

        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets

        with self.use_cassette():
            styles = {"headerColor": "#123456", "backgroundColor": "#bb0e00"}
            config = {
                "numEvents": 10,
                "showDate": True,
                "showDescription": False,
                "showLocation": False,
                "showTime": True,
                "showTitle": True,
            }
            cal_id = "ccahu0rstno2jrvioq4ccffn78@group.calendar.google.com"
            widget = widgets.mod.add_calendar(
                "Upcoming Events", cal_id, True, config, styles
            )

            assert isinstance(widget, Calendar)
            assert widget.shortName == "Upcoming Events"
            assert (
                widget.googleCalendarId
                == "ccahu0rstno2jrvioq4ccffn78@group.calendar.google.com"
            )
            assert widget.configuration == config
            assert widget.styles == styles

            widget = widget.mod.update(shortName="Past Events :(")

            assert isinstance(widget, Calendar)
            assert widget.shortName == "Past Events :("
            assert (
                widget.googleCalendarId
                == "ccahu0rstno2jrvioq4ccffn78@group.calendar.google.com"
            )
            assert widget.configuration == config
            assert widget.styles == styles

            widget.mod.delete()


class TestCommunityList(IntegrationTest):
    def test_community_list(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            comm_list = None
            for widget in widgets.sidebar:
                if isinstance(widget, CommunityList):
                    comm_list = widget
                    break
            assert isinstance(comm_list, CommunityList)
            assert len(comm_list) >= 1
            assert all(isinstance(subreddit, Subreddit) for subreddit in comm_list)
            assert comm_list == comm_list
            assert comm_list.id == comm_list
            assert comm_list in widgets.sidebar

            assert comm_list.shortName
            assert comm_list[0] in comm_list

            assert subreddit == comm_list.subreddit

    @mock.patch("time.sleep", return_value=None)
    def test_create_and_update_and_delete(self, _):
        self.reddit.read_only = False

        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets

        with self.use_cassette():
            styles = {"headerColor": "#123456", "backgroundColor": "#bb0e00"}
            subreddits = ["learnpython", self.reddit.subreddit("redditdev")]
            widget = widgets.mod.add_community_list(
                "My fav subs", subreddits, styles, "My description"
            )

            assert isinstance(widget, CommunityList)
            assert widget.shortName == "My fav subs"
            assert widget.styles == styles
            assert widget.description == "My description"
            assert self.reddit.subreddit("learnpython") in widget
            assert "redditdev" in widget

            widget = widget.mod.update(
                shortName="My least fav subs :(",
                data=["redesign"],
                description="My new description",
            )

            assert isinstance(widget, CommunityList)
            assert widget.shortName == "My least fav subs :("
            assert widget.styles == styles
            assert widget.description == "My new description"
            assert self.reddit.subreddit("redesign") in widget

            widget.mod.delete()


class TestCustomWidget(IntegrationTest):
    @staticmethod
    def image_path(name):
        test_dir = abspath(dirname(sys.modules[__name__].__file__))
        return join(test_dir, "..", "..", "files", name)

    @mock.patch("time.sleep", return_value=None)
    def test_create_and_update_and_delete(self, _):
        self.reddit.read_only = False

        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets

        with self.use_cassette():
            image_dicts = [
                {
                    "width": 0,
                    "height": 0,
                    "name": "a",
                    "url": widgets.mod.upload_image(self.image_path("test.png")),
                }
            ]

            styles = {"headerColor": "#123456", "backgroundColor": "#bb0e00"}
            widget = widgets.mod.add_custom_widget(
                "My widget", "# Hello world!", "/**/", 200, image_dicts, styles
            )

            assert isinstance(widget, CustomWidget)
            assert widget.shortName == "My widget"
            assert widget.text == "# Hello world!"
            assert widget.css == "/**/"
            assert widget.height == 200
            assert widget.styles == styles
            assert len(widget.imageData) == 1
            assert all(isinstance(img, ImageData) for img in widget.imageData)

            # initially, image URLs are incorrect, so we much refresh to get
            # the proper ones.
            widgets.refresh()
            refreshed = widgets.sidebar[-1]
            assert refreshed == widget
            widget = refreshed

            new_css = "h1,h2,h3,h4,h5,h6 {color: #00ff00;}"
            widget = widget.mod.update(css=new_css)

            assert isinstance(widget, CustomWidget)
            assert widget.shortName == "My widget"
            assert widget.text == "# Hello world!"
            assert widget.css == new_css
            assert widget.height == 200
            assert widget.styles == styles
            assert len(widget.imageData) == 1
            assert all(isinstance(img, ImageData) for img in widget.imageData)

            widget.mod.delete()

    def test_custom_widget(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            custom = None
            for widget in widgets.sidebar:
                if isinstance(widget, CustomWidget):
                    custom = widget
                    break
            assert isinstance(custom, CustomWidget)
            assert len(custom.imageData) > 0
            assert all(isinstance(img_data, ImageData) for img_data in custom.imageData)
            assert custom == custom
            assert custom.id == custom
            assert custom in widgets.sidebar

            assert 500 >= custom.height >= 50
            assert custom.text
            assert custom.css
            assert custom.shortName

            assert subreddit == custom.subreddit


class TestIDCard(IntegrationTest):
    def test_id_card(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            card = widgets.id_card
            assert isinstance(card, IDCard)
            assert card == card
            assert card.id == card

            assert card.shortName
            assert card.currentlyViewingText
            assert card.subscribersText

            assert subreddit == card.subreddit

    @mock.patch("time.sleep", return_value=None)
    def test_update(self, _):
        self.reddit.read_only = False

        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette():
            assert widgets.id_card.currentlyViewingText != "Users here NOW!"
            assert widgets.id_card.subscribersText != "Loyal readers"

            widgets.id_card.mod.update(currentlyViewingText="Users here NOW!")
            widgets.refresh()

            assert widgets.id_card.currentlyViewingText == "Users here NOW!"
            assert widgets.id_card.subscribersText != "Loyal readers"

            widgets.id_card.mod.update(subscribersText="Loyal readers")
            widgets.refresh()

            assert widgets.id_card.currentlyViewingText == "Users here NOW!"
            assert widgets.id_card.subscribersText == "Loyal readers"


class TestImageWidget(IntegrationTest):
    @staticmethod
    def image_path(name):
        test_dir = abspath(dirname(sys.modules[__name__].__file__))
        return join(test_dir, "..", "..", "files", name)

    @mock.patch("time.sleep", return_value=None)
    def test_create_and_update_and_delete(self, _):
        self.reddit.read_only = False

        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets

        with self.use_cassette():
            image_paths = (self.image_path(name) for name in ("test.jpg", "test.png"))
            image_dicts = [
                {
                    "width": 0,
                    "height": 0,
                    "linkUrl": "",
                    "url": widgets.mod.upload_image(img_path),
                }
                for img_path in image_paths
            ]

            styles = {"headerColor": "#123456", "backgroundColor": "#bb0e00"}
            widget = widgets.mod.add_image_widget(
                short_name="My new pics!", data=image_dicts, styles=styles
            )

            assert isinstance(widget, ImageWidget)
            assert widget.shortName == "My new pics!"
            assert widget.styles == styles
            assert len(widget) == 2
            assert all(isinstance(img, Image) for img in widget)

            widget = widget.mod.update(shortName="My old pics :(", data=image_dicts[:1])

            assert isinstance(widget, ImageWidget)
            assert widget.shortName == "My old pics :("
            assert widget.styles == styles
            assert len(widget) == 1
            assert all(isinstance(img, Image) for img in widget)

            widget.mod.delete()

    def test_image_widget(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            img_widget = None
            for widget in widgets.sidebar:
                if isinstance(widget, ImageWidget):
                    img_widget = widget
                    break
            assert isinstance(img_widget, ImageWidget)
            assert len(img_widget) >= 1
            assert all(isinstance(image, Image) for image in img_widget)
            assert img_widget == img_widget
            assert img_widget.id == img_widget
            assert img_widget in widgets.sidebar

            assert img_widget[0].linkUrl
            assert img_widget.shortName

            assert subreddit == img_widget.subreddit


class TestMenu(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_create_and_update_and_delete(self, _):
        self.reddit.read_only = False

        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets

        menu_contents = [
            {"text": "My homepage", "url": "https://example.com"},
            {
                "text": "Python packages",
                "children": [
                    {"text": "PRAW", "url": "https://praw.readthedocs.io/"},
                    {"text": "requests", "url": "http://python-requests.org"},
                ],
            },
            {"text": "Reddit homepage", "url": "https://reddit.com"},
        ]

        with self.use_cassette():
            widget = widgets.mod.add_menu(menu_contents)

            assert isinstance(widget, Menu)
            assert len(widget) == 3
            assert all(isinstance(item, (Submenu, MenuLink)) for item in widget)
            assert all(
                all(isinstance(item, MenuLink) for item in subm)
                for subm in widget
                if isinstance(subm, Submenu)
            )

            assert widget[0].text == "My homepage"
            assert widget[0].url == "https://example.com"
            assert widget[2].text == "Reddit homepage"
            assert widget[2].url == "https://reddit.com"

            assert widget[1].text == "Python packages"
            assert widget[1][0].text == "PRAW"
            assert widget[1][0].url == "https://praw.readthedocs.io/"
            assert widget[1][1].text == "requests"
            assert widget[1][1].url == "http://python-requests.org"

            menu_contents.reverse()
            widget = widget.mod.update(data=menu_contents)

            assert isinstance(widget, Menu)
            assert len(widget) == 3
            assert all(isinstance(item, (Submenu, MenuLink)) for item in widget)
            assert all(
                all(isinstance(item, MenuLink) for item in subm)
                for subm in widget
                if isinstance(subm, Submenu)
            )

            assert widget[0].text == "Reddit homepage"
            assert widget[0].url == "https://reddit.com"
            assert widget[2].text == "My homepage"
            assert widget[2].url == "https://example.com"

            assert widget[1].text == "Python packages"
            assert widget[1][0].text == "PRAW"
            assert widget[1][0].url == "https://praw.readthedocs.io/"
            assert widget[1][1].text == "requests"
            assert widget[1][1].url == "http://python-requests.org"

            widget.mod.delete()

    def test_menu(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            menu = None
            for widget in widgets.topbar:
                if isinstance(widget, Menu):
                    menu = widget
                    break
            assert isinstance(menu, Menu)
            assert all(isinstance(item, (MenuLink, Submenu)) for item in menu)
            assert menu == menu
            assert menu.id == menu
            assert menu in widgets.topbar
            assert len(menu) >= 1
            assert menu[0].text

            assert subreddit == menu.subreddit

            submenu = None
            for child in menu:
                if isinstance(child, Submenu):
                    submenu = child
                    break
            assert isinstance(submenu, Submenu)
            assert len(submenu) >= 0
            assert all(isinstance(child, MenuLink) for child in submenu)
            assert submenu[0].text
            assert submenu[0].url


class TestModeratorsWidget(IntegrationTest):
    def test_moderators_widget(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            mods = widgets.moderators_widget
            assert isinstance(mods, ModeratorsWidget)
            assert all(isinstance(mod, Redditor) for mod in mods)
            assert mods == mods
            assert mods.id == mods

            assert len(mods) >= 1
            assert isinstance(mods[0], Redditor)

            assert subreddit == mods.subreddit

    @mock.patch("time.sleep", return_value=None)
    def test_update(self, _):
        self.reddit.read_only = False

        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        new_styles = {"backgroundColor": "#bababa", "headerColor": "#407bee"}
        with self.use_cassette():
            assert widgets.moderators_widget.styles != new_styles

            widgets.moderators_widget.mod.update(styles=new_styles)
            widgets.refresh()

            assert widgets.moderators_widget.styles == new_styles


class TestPostFlairWidget(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_create_and_update_and_delete(self, _):
        self.reddit.read_only = False

        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets

        with self.use_cassette():
            flairs = [f["id"] for f in subreddit.flair.link_templates][:30]

            styles = {"headerColor": "#123456", "backgroundColor": "#bb0e00"}
            widget = widgets.mod.add_post_flair_widget(
                "Some flairs", "list", flairs, styles
            )

            assert isinstance(widget, PostFlairWidget)
            assert widget.shortName == "Some flairs"
            assert widget.display == "list"
            assert widget.order == flairs
            assert widget.styles == styles
            assert len(widget) == len(flairs)
            assert all(flair_id in widget.templates for flair_id in widget)

            widget = widget.mod.update(display="cloud")

            assert isinstance(widget, PostFlairWidget)
            assert widget.shortName == "Some flairs"
            assert widget.display == "cloud"
            assert widget.order == flairs
            assert widget.styles == styles
            assert len(widget) == len(flairs)
            assert all(flair_id in widget.templates for flair_id in widget)

            widget = widget.mod.update(order=widget.order[:1])

            assert isinstance(widget, PostFlairWidget)
            assert widget.shortName == "Some flairs"
            assert widget.display == "cloud"
            assert widget.order == flairs[:1]
            assert widget.styles == styles
            assert len(widget) == 1
            assert all(flair_id in widget.templates for flair_id in widget)

            widget.mod.delete()

    def test_post_flair_widget(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            pf_widget = None
            for widget in widgets.sidebar:
                if isinstance(widget, PostFlairWidget):
                    pf_widget = widget
                    break
            assert isinstance(pf_widget, PostFlairWidget)
            assert len(pf_widget) >= 1
            assert all(flair_id in widget.templates for flair_id in widget)
            assert pf_widget == pf_widget
            assert pf_widget.id == pf_widget
            assert pf_widget in widgets.sidebar

            assert pf_widget.shortName
            assert all(flair in pf_widget for flair in pf_widget)

            assert subreddit == pf_widget.subreddit


class TestRulesWidget(IntegrationTest):
    def test_rules_widget(self):

        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            rules = None
            for widget in widgets.sidebar:
                if isinstance(widget, RulesWidget):
                    rules = widget
                    break
            assert isinstance(rules, RulesWidget)
            assert rules == rules
            assert rules.id == rules

            assert rules.display

            assert len(rules) > 0
            assert subreddit == rules.subreddit

    @mock.patch("time.sleep", return_value=None)
    def test_update(self, _):
        self.reddit.read_only = False

        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        new_styles = {"backgroundColor": "#fedcba", "headerColor": "#012345"}
        with self.use_cassette():
            rules = None
            for widget in widgets.sidebar:
                if isinstance(widget, RulesWidget):
                    rules = widget
                    break
            assert isinstance(rules, RulesWidget)

            assert rules.shortName != "Our regulations"
            assert rules.styles != new_styles

            rules = rules.mod.update(
                display="compact",
                shortName="Our regulations",
                styles=new_styles,
            )

            assert rules.display == "compact"
            assert rules.shortName == "Our regulations"
            assert rules.styles == new_styles


class TestSubredditWidgets(IntegrationTest):
    def test_bad_attribute(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            with pytest.raises(AttributeError):
                widgets.nonexistant_attribute

    def test_items(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            assert isinstance(widgets.items, dict)

    def test_progressive_images(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets

        def has_progressive(widgets_):
            # best way I could figure if an image is progressive
            sign = "fm=pjpg"

            for widget in widgets_.sidebar:
                if isinstance(widget, ImageWidget):
                    for image in widget:
                        if sign in image.url:
                            return True
                elif isinstance(widget, CustomWidget):
                    for image_data in widget.imageData:
                        if sign in image_data.url:
                            return True

            return False

        with self.use_cassette():
            widgets.progressive_images = True
            assert has_progressive(widgets)
            widgets.progressive_images = False
            widgets.refresh()
            assert not has_progressive(widgets)
            widgets.progressive_images = True
            widgets.refresh()
            assert has_progressive(widgets)

    def test_refresh(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette():
            assert widgets.sidebar  # to fetch
            old_sidebar = widgets.sidebar  # reference, not value
            widgets.refresh()
            assert old_sidebar is not widgets.sidebar  # should be new list

    def test_repr(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        assert (
            f"SubredditWidgets(subreddit=Subreddit(display_name='{pytest.placeholders.test_subreddit}'))"
            == repr(widgets)
        )

    def test_sidebar(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            assert len(widgets.sidebar) >= 1  # also tests lazy-loading

        # all items should be Widget subclasses
        assert all(
            isinstance(widget, Widget) and type(widget) != Widget
            for widget in widgets.sidebar
        )

    def test_specials(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            assert isinstance(widgets.id_card, IDCard)
            assert isinstance(widgets.moderators_widget, ModeratorsWidget)

    def test_topbar(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            assert 1 <= len(widgets.topbar)
            assert all(
                isinstance(widget, Widget) and type(widget) != Widget
                for widget in widgets.topbar
            )


class TestSubredditWidgetsModeration(IntegrationTest):
    @staticmethod
    def image_path(name):
        test_dir = abspath(dirname(sys.modules[__name__].__file__))
        return join(test_dir, "..", "..", "files", name)

    @mock.patch("time.sleep", return_value=None)
    def test_reorder(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets

        with self.use_cassette():
            old_order = list(widgets.sidebar)
            new_order = list(reversed(old_order))

            widgets.mod.reorder(new_order)
            widgets.refresh()
            assert list(widgets.sidebar) == new_order

            widgets.mod.reorder(old_order)
            widgets.refresh()
            assert list(widgets.sidebar) == old_order

            mixed_types = [
                thing if i % 2 == 0 else thing.id for i, thing in enumerate(new_order)
            ]
            # mixed_types has some str and some Widget.
            assert any(isinstance(thing, basestring) for thing in mixed_types)
            assert any(isinstance(thing, Widget) for thing in mixed_types)

            widgets.mod.reorder(mixed_types)
            widgets.refresh()
            assert list(widgets.sidebar) == new_order

    @mock.patch("time.sleep", return_value=None)
    def test_upload_image(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets

        with self.use_cassette():
            for image in ("test.jpg", "test.png"):
                image_url = widgets.mod.upload_image(self.image_path(image))
                assert image_url


class TestTextArea(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_create_and_update_and_delete(self, _):
        self.reddit.read_only = False

        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets

        with self.use_cassette():
            styles = {"headerColor": "#123456", "backgroundColor": "#bb0e00"}
            widget = widgets.mod.add_text_area(
                short_name="My new widget!", text="Hello world!", styles=styles
            )

            assert isinstance(widget, TextArea)
            assert widget.shortName == "My new widget!"
            assert widget.styles == styles
            assert widget.text == "Hello world!"

            widget = widget.mod.update(shortName="My old widget :(", text="Feed me")

            assert isinstance(widget, TextArea)
            assert widget.shortName == "My old widget :("
            assert widget.styles == styles
            assert widget.text == "Feed me"

            widget.mod.delete()

    def test_text_area(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            text = None
            for widget in widgets.sidebar:
                if isinstance(widget, TextArea):
                    text = widget
                    break
            assert isinstance(text, TextArea)
            assert text == text
            assert text.id == text
            assert text in widgets.sidebar
            assert text in widgets.sidebar

            assert text.shortName
            assert text.text

            assert subreddit == text.subreddit


class TestWidget(IntegrationTest):
    def test_inequality(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.use_cassette("TestSubredditWidgets.fetch_widgets"):
            assert len(widgets.sidebar) >= 2
        assert widgets.sidebar[0] != widgets.sidebar[1]
        assert widgets.sidebar[0] != widgets.sidebar[1].id
