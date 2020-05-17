from json import dumps

from pytest import raises

from praw.models import (
    Button,
    Styles,
    SubredditWidgets,
    SubredditWidgetsModeration,
    Widget,
    WidgetModeration,
)
from praw.models.base import PRAWBase
from praw.models.reddit.widgets import WidgetEncoder

from ... import UnitTest


class TestStyles(UnitTest):
    def test_convert_rgb_int_to_string(self):
        assert (
            Styles.convert_rgb_int_to_string(0xFFFFFF).lower()
            == "#FFFFFF".lower()
        )
        assert (
            Styles.convert_rgb_int_to_string(0xAABBCC).lower()
            == "#AABBCC".lower()
        )

    def test_convert_rgb_int_to_string_invalid(self):
        with raises(ValueError) as excinfo:
            Styles.convert_rgb_int_to_string(-1)
        assert (
            excinfo.value.args[0]
            == "The given integer (-1) is greater than 16777215 or less than "
            "0."
        )
        with raises(ValueError) as excinfo:
            Styles.convert_rgb_int_to_string(0xFFFFFF + 1)
        assert (
            excinfo.value.args[0]
            == "The given integer (16777216) is greater than 16777215 or less"
            " than 0."
        )

    def test_convert_rgb_string_to_int(self):
        assert Styles.convert_rgb_string_to_int("#FFFFFF") == 0xFFFFFF
        assert Styles.convert_rgb_string_to_int("#AABBCC") == 0xAABBCC

    def test_convert_rgb_string_to_int_invalid(self):
        with raises(ValueError) as excinfo:
            Styles.convert_rgb_string_to_int("Test")
        assert (
            excinfo.value.args[0]
            == "An hxadecimal string ``#XXXXXX`` was not specified, instead "
            "'Test' was specified"
        )


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

    def test_equality(self):
        b = Button(self.reddit, {})
        w = Widget(self.reddit, {})
        assert not (b == w)

    def test_repr(self):
        w = Widget(self.reddit, {})
        assert repr(w) == "<Widget widget>"

    def test_conversion(self):
        example = [
            {"test": {"testColor": 16777215}},
            [{"testColor": 16777215}],
        ]
        conversion_method = (
            SubredditWidgetsModeration._convert_color_list_to_RGB
        )
        converted = conversion_method(example)
        assert isinstance(converted[0]["test"]["testColor"], str)
        assert isinstance(converted[1][0]["testColor"], str)
