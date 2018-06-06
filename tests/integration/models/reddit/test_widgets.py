import pytest

from praw.models import (Button, ButtonWidget, Calendar, CommunityList,
                         CustomWidget, Menu, MenuLink, IDCard, Image,
                         ImageData, ImageWidget, ModeratorsWidget, Redditor,
                         RulesWidget, Submenu, Subreddit, TextArea, Widget)
from ... import IntegrationTest


class TestButtonWidget(IntegrationTest):

    def test_button_widget(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
            button_widget = None
            for widget in widgets.sidebar:
                if isinstance(widget, ButtonWidget):
                    button_widget = widget
                    break
            assert isinstance(button_widget, ButtonWidget)
            assert len(button_widget) >= 1
            assert all(isinstance(button, Button) for button in
                       button_widget.buttons)
            assert button_widget == button_widget
            assert button_widget.id == button_widget
            assert button_widget in widgets.sidebar

            assert button_widget[0].text
            assert button_widget.shortName
            assert hasattr(button_widget, 'description')

            assert subreddit == button_widget.subreddit


class TestCalendar(IntegrationTest):

    def test_calendar(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
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
            assert hasattr(calendar, 'requiresSync')

            assert subreddit == calendar.subreddit


class TestCommunityList(IntegrationTest):

    def test_community_list(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
            comm_list = None
            for widget in widgets.sidebar:
                if isinstance(widget, CommunityList):
                    comm_list = widget
                    break
            assert isinstance(comm_list, CommunityList)
            assert len(comm_list) >= 1
            assert all(isinstance(subreddit, Subreddit) for subreddit in
                       comm_list)
            assert comm_list == comm_list
            assert comm_list.id == comm_list
            assert comm_list in widgets.sidebar

            assert comm_list.shortName
            assert comm_list[0] in comm_list

            assert subreddit == comm_list.subreddit


class TestCustomWidget(IntegrationTest):

    def test_custom_widget(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
            custom = None
            for widget in widgets.sidebar:
                if isinstance(widget, CustomWidget):
                    custom = widget
                    break
            assert isinstance(custom, CustomWidget)
            assert len(custom.imageData) > 0
            assert all(isinstance(img_data, ImageData) for img_data in
                       custom.imageData)
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
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
            card = widgets.id_card
            assert isinstance(card, IDCard)
            assert card == card
            assert card.id == card

            assert card.shortName
            assert card.currentlyViewingText
            assert card.subscribersText

            assert subreddit == card.subreddit


class TestImageWidget(IntegrationTest):

    def test_image_widget(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
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

    def test_menu(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
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
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
            mods = widgets.moderators_widget
            assert isinstance(mods, ModeratorsWidget)
            assert all(isinstance(mod, Redditor) for mod in mods)
            assert mods == mods
            assert mods.id == mods

            assert len(mods) >= 1
            assert isinstance(mods[0], Redditor)

            assert subreddit == mods.subreddit


class TestRulesWidget(IntegrationTest):

    def test_rules_widget(self):

        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
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


class TestSubredditWidgets(IntegrationTest):
    def test_bad_attribute(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
            with pytest.raises(AttributeError):
                widgets.nonexistant_attribute

    def test_items(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
            assert isinstance(widgets.items, dict)

    def test_progressive_images(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets

        def has_progressive(widgets_):
            # best way I could figure if an image is progressive
            sign = 'fm=pjpg'

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

        with self.recorder.use_cassette(
                'TestSubredditWidgets.test_progressive_images'):
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
        with self.recorder.use_cassette('TestSubredditWidgets.test_refresh'):
            assert widgets.sidebar  # to fetch
            old_sidebar = widgets.sidebar  # reference, not value
            widgets.refresh()
            assert old_sidebar is not widgets.sidebar  # should be new list

    def test_repr(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        assert ("SubredditWidgets(subreddit=Subreddit(display_name='"
                "{}'))").format(pytest.placeholders.test_subreddit) == repr(
            widgets)

    def test_sidebar(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
            assert len(widgets.sidebar) >= 1  # also tests lazy-loading

        # all items should be Widget subclasses
        assert all(isinstance(widget, Widget) and type(widget) != Widget
                   for widget in widgets.sidebar)

    def test_specials(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
            assert isinstance(widgets.id_card, IDCard)
            assert isinstance(widgets.moderators_widget, ModeratorsWidget)

    def test_topbar(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
            assert 1 <= len(widgets.topbar)
            assert all(isinstance(widget, Widget) and type(widget) != Widget
                       for widget in widgets.topbar)


class TestTextArea(IntegrationTest):

    def test_text_area(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
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
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
            assert len(widgets.sidebar) >= 2
        assert widgets.sidebar[0] != widgets.sidebar[1]
        assert widgets.sidebar[0] != widgets.sidebar[1].id
        assert u'\xf0\x9f\x98\x80' != widgets.sidebar[0]  # for python 2
