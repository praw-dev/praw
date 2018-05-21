import mock
import pytest
from copy import copy

from prawcore.exceptions import BadRequest
from praw.models import (Button, ButtonWidget, Calendar, CommunityList,
                         CustomWidget, Menu, MenuLink, IDCard, Image,
                         ImageData, ImageWidget, ModeratorsWidget, Redditor,
                         RulesWidget, Submenu, Subreddit, TextArea, Widget)
from ... import IntegrationTest


class TestButton(IntegrationTest):
    def test_button(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        button = widgets.button('Click me!', 'https://duckduckgo.com',
                                '#ff0000')
        assert isinstance(button, Button)
        assert 'Click me!' == button.text
        assert 'https://duckduckgo.com' == button.url
        assert '#ff0000' == button.color
        assert ("Button(text='Click me!', url='https://duckduckgo.com', "
                "color='#ff0000')") == repr(button)
        assert 'Click me!' == str(button)


class TestButtonWidget(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_button_widget(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestButtonWidget.test_button_widget'):
            button_widget = widgets.create_button_widget('My buttons', [
                widgets.button('PRAW', 'https://github.com/praw-dev/praw',
                               '#aa11aa')
            ], 'One button.')
            assert isinstance(button_widget, ButtonWidget)
            assert all(isinstance(button, Button) for button in
                       button_widget.buttons)
            assert button_widget == button_widget
            assert button_widget.id == button_widget
            assert button_widget in widgets.sidebar
            assert "ButtonWidget(id='{}')".format(button_widget.id) == repr(
                button_widget)
            assert button_widget.id == str(button_widget)
            assert 1 == len(button_widget)
            assert 'PRAW' == button_widget[0].text
            button_widget.update(buttons=button_widget.buttons * 2)
            assert 2 == len(button_widget)
            assert 'My buttons' == button_widget.shortName

            button_widget.update(description='Some buttons for you.')
            assert 'Some buttons for you.' == button_widget.description
            assert 2 == len(button_widget)

            assert all(isinstance(button, Button) for button in
                       button_widget.buttons)

            button_widget.delete()

            widgets()
            assert button_widget not in widgets.sidebar


class TestCalendar(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_calendar(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        cal_id = ('nytimes.com_c9hche3raajglitokho7rvu664@group.calendar'
                  '.google.com')
        with self.recorder.use_cassette('TestCalendar.test_calendar'):
            calendar = widgets.create_calendar('2016 election', cal_id)
            assert isinstance(calendar, Calendar)
            assert calendar == calendar
            assert calendar.id == calendar
            assert calendar in widgets.sidebar
            assert "Calendar(id='{}')".format(calendar.id) == repr(calendar)
            assert calendar.id == str(calendar)
            calendar.update(show_time=False)
            assert calendar.configuration['showTime'] is False
            calendar.update(show_time=False)
            assert cal_id == calendar.googleCalendarId
            calendar.update(show_time=True)
            assert calendar.configuration['showTime'] is True

            calendar.delete()

            widgets()
            assert calendar not in widgets.sidebar


class TestCommunityList(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_community_list(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette(
                'TestCommunityList.test_community_list'):
            comm_list = widgets.create_community_list('Popular Subreddits',
                                                      ['tifu', 'funny',
                                                       'atbge',
                                                       self.reddit.subreddit(
                                                           'videos')])
            assert isinstance(comm_list, CommunityList)
            assert all(isinstance(subreddit, Subreddit) for subreddit in
                       comm_list.subreddits)
            assert comm_list == comm_list
            assert comm_list.id == comm_list
            assert comm_list in widgets.sidebar
            assert "CommunityList(id='{}')".format(comm_list.id) == repr(
                comm_list)
            assert comm_list.id == str(comm_list)
            assert 4 == len(comm_list)
            assert 'videos' in comm_list.subreddits
            assert 'TIFU' in comm_list.subreddits
            assert 'videos' == comm_list[3]

            comm_list.update(subreddits=comm_list.subreddits[:2])
            assert 2 == len(comm_list)
            assert 'Popular Subreddits' == comm_list.shortName

            comm_list.update(short_name='PopSubs')
            assert 'PopSubs' == comm_list.shortName
            assert 2 == len(comm_list)

            comm_list.delete()

            widgets()
            assert comm_list not in widgets.sidebar


class TestCustomWidget(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_custom_widget(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestCustomWidget.test_custom_widget'):
            custom = widgets.create_custom_widget('Name not displayed',
                                                  300,
                                                  'This *is* the text\n\nyes?',
                                                  'em {color: #ff00ff;}')
            assert isinstance(custom, CustomWidget)
            assert all(isinstance(img_data, ImageData) for img_data in
                       custom.imageData)
            assert custom == custom
            assert custom.id == custom
            assert custom in widgets.sidebar
            assert "CustomWidget(id='{}')".format(custom.id) == repr(custom)
            assert custom.id == str(custom)

            assert 300 == custom.height
            assert 'This *is* the text\n\nyes?' == custom.text
            assert 'em {color: #ff00ff;}' == custom.css
            custom.update(text='*This* text is new!')
            assert 'Name not displayed' == custom.shortName
            assert 'em {color: #ff00ff;}' == custom.css
            assert '*This* text is new!' == custom.text

            custom.update(short_name='Invisible')
            assert 'Invisible' == custom.shortName
            assert '*This* text is new!' == custom.text
            assert all(isinstance(img_data, ImageData) for img_data in
                       custom.imageData)

            custom.delete()

            widgets()
            assert custom not in widgets.sidebar


class TestIDCard(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_id_card(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestIDCard.test_id_card'):
            card = widgets.id_card
            assert isinstance(card, IDCard)
            assert card == card
            assert card.id == card
            assert "IDCard(id='{}')".format(card.id) == repr(card)
            assert card.id == str(card)

            subscribers_text = card.subscribersText
            card.update(short_name='Where am I?',
                        currently_viewing_text='Rabid fans')
            assert 'Where am I?' == card.shortName
            assert 'Rabid fans' == card.currentlyViewingText
            assert subscribers_text == card.subscribersText

            card.update(subscribers_text='Ghosts')
            assert 'Where am I?' == card.shortName
            assert 'Ghosts' == card.subscribersText
            assert 'Rabid fans' == card.currentlyViewingText

            with pytest.raises(BadRequest):  # cannot delete it
                card.delete()

            widgets()
            assert widgets.id_card == card


class TestImage(IntegrationTest):
    def test_image(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        image = widgets.image('https://example.com', 600, 400)
        assert isinstance(image, Image)
        assert 600 == image.width
        assert 400 == image.height
        assert 'https://example.com' == image.url
        assert 'https://example.com' == str(image)
        assert "Image(url='https://example.com', width=600, height=400)" == \
               repr(image)

        image = widgets.image('https://example.com', 700, 500,
                              'https://google.com')
        assert isinstance(image, Image)
        assert 700 == image.width
        assert 500 == image.height
        assert 'https://example.com' == image.url
        assert 'https://google.com' == image.linkUrl
        assert 'https://example.com' == str(image)
        assert ("Image(url='https://example.com', width=700, height=500, "
                "linkUrl='https://google.com')") == repr(image)


class TestImageData(IntegrationTest):
    def test_image_data(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        image_data = widgets.image_data('https://example.com/img.png',
                                        'mypic',
                                        200, 200)
        assert isinstance(image_data, ImageData)
        assert 200 == image_data.width
        assert 200 == image_data.height
        assert 'https://example.com/img.png' == image_data.url
        assert 'mypic' == image_data.name
        assert ("ImageData(url='https://example.com/img.png', "
                "name='mypic', width=200, height=200)") == repr(image_data)
        assert 'mypic' == str(image_data)


class TestImageWidget(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_image_widget(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestImageWidget.test_image_widget'):
            link = widgets.upload_image('tests/integration/files/test.jpg')
            image = widgets.image(link, 128, 128, 'https://reddit.com')
            img_widget = widgets.create_image_widget('Cool pix', [image])
            assert all(isinstance(image, Image) for image in img_widget.images)
            assert isinstance(img_widget, ImageWidget)
            assert img_widget == img_widget
            assert img_widget.id == img_widget
            assert img_widget in widgets.sidebar
            assert "ImageWidget(id='{}')".format(img_widget.id) == repr(
                img_widget)
            assert img_widget.id == str(img_widget)
            assert 1 == len(img_widget)
            assert 'https://reddit.com' == img_widget[0].linkUrl
            img_widget.update(images=img_widget.images * 2)
            assert 2 == len(img_widget)
            assert 'Cool pix' == img_widget.shortName

            img_widget.update(short_name='Uncool pix')
            assert 'Uncool pix' == img_widget.shortName
            assert 2 == len(img_widget)
            assert all(isinstance(image, Image) for image in img_widget.images)

            img_widget.delete()

            widgets()
            assert img_widget not in widgets.sidebar


class TestMenu(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_menu(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestMenu.test_menu'):
            widgets = subreddit.widgets()
            if widgets.topbar:  # should be just one item
                widgets.topbar[0].delete()
            menu = widgets.create_menu([
                widgets.menu_link('https://reddit.com/r/redditdev/', 'rdev'),
                widgets.submenu('PRAW', [
                    widgets.menu_link('https://github.com/praw-dev/praw/',
                                      'Source'),
                    widgets.menu_link('https://praw.readthedocs.io', 'Docs')
                ])])
            assert all(isinstance(item, (MenuLink, Submenu)) for item in
                       menu.children)
            assert isinstance(menu, Menu)
            assert menu == menu
            assert menu.id == menu
            widgets()
            assert menu in widgets.topbar
            assert "Menu(id='{}')".format(menu.id) == repr(menu)
            assert menu.id == str(menu)
            assert 2 == len(menu)
            assert 'https://reddit.com/r/redditdev/' == menu.children[0].url
            menu.update(contents=menu.children[1:])
            assert 1 == len(menu)

            assert all(isinstance(item, (MenuLink, Submenu)) for item in
                       menu.children)

            menu.delete()

            widgets()
            assert menu not in widgets.topbar


class TestMenuLink(IntegrationTest):
    def test_menu_link(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        menu_link = widgets.menu_link('https://google.com', 'Google')
        assert isinstance(menu_link, MenuLink)
        assert 'Google' == menu_link.text
        assert 'https://google.com' == menu_link.url
        assert "MenuLink(text='Google', url='https://google.com')" == repr(
            menu_link)
        assert 'Google' == str(menu_link)


class TestModeratorsWidget(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_moderators_widget(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette(
                'TestModeratorsWidget.test_moderators_widget'):
            mods = widgets.moderators_widget
            assert isinstance(mods, ModeratorsWidget)
            assert all(isinstance(mod, Redditor) for mod in mods.moderators)
            assert mods == mods
            assert mods.id == mods
            assert "ModeratorsWidget(id='{}')".format(mods.id) == repr(mods)
            assert mods.id == str(mods)

            assert 1 <= len(mods)
            assert isinstance(mods[0], Redditor)
            assert self.reddit.user.me() in mods.moderators

            with pytest.raises(BadRequest):  # cannot delete it
                mods.delete()

            widgets()
            assert widgets.moderators_widget == mods


class TestRulesWidget(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_rules_widget(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestRulesWidget.test_rules_widget'):
            rules = None
            for widget in widgets.sidebar:
                if isinstance(widget, RulesWidget):
                    rules = widget
                    break
            assert isinstance(rules, RulesWidget), "couldn't get rules widget"
            assert rules == rules
            assert rules.id == rules
            assert "RulesWidget(id='{}')".format(rules.id) == repr(rules)
            assert rules.id == str(rules)

            rules.update(display='full')
            assert 'full' == rules.display
            rules.update(display='compact')
            assert 'compact' == rules.display

            widgets()
            assert rules in widgets.sidebar

            with pytest.raises(BadRequest):  # cannot delete it
                rules.delete()

            widgets()
            assert rules in widgets.sidebar


class TestSubmenu(IntegrationTest):
    def test_submenu(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        submenu = widgets.submenu('OSS',
                                  [widgets.menu_link(
                                      'https://github.com/praw-dev/praw',
                                      'PRAW')])
        assert isinstance(submenu, Submenu)
        assert 'OSS' == submenu.text
        assert 1 == len(submenu)
        assert 'PRAW' == submenu[0].text
        assert "Submenu(text='OSS')" == repr(submenu)
        assert 'OSS' == str(submenu)


class TestSubredditWidgets(IntegrationTest):
    def test_bad_attribute(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
            with pytest.raises(AttributeError):
                widgets.nonexistant_attribute

    def test_calls_return_same_object(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
            assert widgets is widgets()

    def test_create_button_widget(self):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        buttons = [widgets.button('Google', 'https://google.com',
                                  '#0000ff'),
                   widgets.button('DuckDuckGo',
                                  'https://duckduckgo.com',
                                  '#ff0000')]
        with self.recorder.use_cassette(
                'TestSubredditWidgets.test_create_button_widget'):
            button_widget = widgets.create_button_widget('Buttons', buttons,
                                                         'search engines')
        assert 'search engines' == button_widget.description
        assert 'Buttons' == button_widget.shortName
        google = button_widget.buttons[0]
        assert 'Google' == google.text
        assert 'https://google.com' == google.url
        assert '#0000ff' == google.color
        ddg = button_widget.buttons[1]
        assert 'DuckDuckGo' == ddg.text
        assert 'https://duckduckgo.com' == ddg.url
        assert '#ff0000' == ddg.color

    def test_create_calendar(self):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        cal_id = ('nytimes.com_c9hche3raajglitokho7rvu664@group.calendar'
                  '.google.com')
        with self.recorder.use_cassette(
                'TestSubredditWidgets.test_create_calendar'):
            calendar = widgets.create_calendar('My great calendar',
                                               cal_id,
                                               show_time=False,
                                               show_location=False)
        assert 'My great calendar' == calendar.shortName
        assert cal_id == calendar.googleCalendarId
        assert calendar.configuration['showDate']
        assert not calendar.configuration['showTime']
        assert not calendar.configuration['showLocation']

    def test_create_community_list(self):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        redditdev = self.reddit.subreddit('redditdev')
        with self.recorder.use_cassette(
                'TestSubredditWidgets.test_create_community_list'):
            community_list = widgets.create_community_list('Other Subreddits',
                                                           [redditdev,
                                                            'programming',
                                                            'LEARNPYTHON'])
        assert all(isinstance(subreddit, Subreddit)
                   for subreddit in community_list.subreddits)
        assert 'Other Subreddits' == community_list.shortName
        assert 3 == len(community_list.subreddits)

    @mock.patch('time.sleep', return_value=None)
    def test_create_custom_widget(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette(
                'TestSubredditWidgets.test_create_custom_widget'):
            image_data = widgets.image_data(
                widgets.upload_image('tests/integration/files/test.png'),
                name='test', width=128, height=128)
            custom = widgets.create_custom_widget('Name not displayed',
                                                  300,
                                                  'This *is* the text\n\nyes?',
                                                  'em {color: #ff00ff;}',
                                                  [image_data])
        assert 'Name not displayed' == custom.shortName
        assert 300 == custom.height
        assert 'This *is* the text\n\nyes?' == custom.text
        assert 'em {color: #ff00ff;}' == custom.css
        assert 1 == len(custom.imageData)
        assert custom.imageData[0].name == 'test'
        assert isinstance(custom.imageData[0], ImageData)

    @mock.patch('time.sleep', return_value=None)
    def test_create_menu(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette(
                'TestSubredditWidgets.test_create_menu'):
            widgets = subreddit.widgets()
            if widgets.topbar:  # should be just one item
                widgets.topbar[0].delete()
            menu = widgets.create_menu([
                widgets.menu_link('https://reddit.com/r/redditdev/', 'rdev'),
                widgets.submenu('PRAW', [
                    widgets.menu_link('https://github.com/praw-dev/praw/',
                                      'Source'),
                    widgets.menu_link('https://praw.readthedocs.io', 'Docs')
                ])])
        assert 2 == len(menu)
        assert isinstance(menu[0], MenuLink)
        assert 'rdev' == menu[0].text
        assert 'https://reddit.com/r/redditdev/' == menu[0].url
        submenu = menu[1]
        assert isinstance(submenu, Submenu)
        assert 2 == len(submenu)
        assert 'https://github.com/praw-dev/praw/' == submenu[0].url
        assert 'Docs' == submenu[1].text

    def test_create_text_area(self):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette(
                'TestSubredditWidgets.test_create_text_area'):
            text_area = widgets.create_text_area('Text area', 'Lorem ipsum')
        assert 'Lorem ipsum' == text_area.text
        assert 'Text area' == text_area.shortName

    @mock.patch('time.sleep', return_value=None)
    def test_reorder(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestSubredditWidgets.test_reorder'):
            widgets = subreddit.widgets()
            original_order = widgets.sidebar[1:]  # first item is "stuck"
            new_order = copy(original_order)
            new_order[2] = new_order[2].id  # ID or object should be valid
            new_order.reverse()
            widgets.reorder(new_order)
            widgets()  # update

        # widgets.sidebar has an extra widget at the front
        # that's not in new_order
        assert new_order[1] == widgets.sidebar[2]
        assert new_order[-1] == widgets.sidebar[-1]

    def test_repr(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        assert "SubredditWidgets(subreddit='{}')".format(
            pytest.placeholders.test_subreddit) == repr(widgets)

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
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
            widgets = subreddit.widgets()
        assert isinstance(widgets.id_card, IDCard)
        assert isinstance(widgets.moderators_widget, ModeratorsWidget)

    def test_topbar(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestSubredditWidgets.fetch_widgets'):
            widgets = subreddit.widgets()
        assert 1 <= len(widgets.topbar)
        assert all(isinstance(widget, Widget) and type(widget) != Widget
                   for widget in widgets.topbar)

    @mock.patch('time.sleep', return_value=None)
    def test_upload_and_create_image_widget(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette(
                'TestSubredditWidgets.upload_and_create'):
            image_links = [
                widgets.upload_image('tests/integration/files/test.png'),
                widgets.upload_image('tests/integration/files/test.jpg')
            ]
            image_objs = [widgets.image(link, 128, 128)
                          for link in image_links]
            images = widgets.create_image_widget('My images', image_objs)
        assert 2 == len(images.data)
        assert 'My images' == images.shortName


class TestTextArea(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_text_area(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        with self.recorder.use_cassette('TestTextArea.test_text_area'):
            text = widgets.create_text_area('Some text',
                                            'Placeholder 1')
            assert isinstance(text, TextArea)
            assert text == text
            assert text.id == text
            assert text in widgets.sidebar
            assert "TextArea(id='{}')".format(text.id) == repr(text)
            assert text.id == str(text)
            text.update(text='2 redlohecalP')
            assert 'Some text' == text.shortName
            assert '2 redlohecalP' == text.text
            text.update(short_name='No text')
            assert 'No text' == text.shortName
            assert '2 redlohecalP' == text.text

            text.delete()

            widgets()
            assert text not in widgets.sidebar
