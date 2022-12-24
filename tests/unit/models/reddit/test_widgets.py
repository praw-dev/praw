from json import dumps

import pytest
from pytest import raises

from praw.models import (
    SubredditWidgets,
    SubredditWidgetsModeration,
    Widget,
    WidgetModeration,
)
from praw.models.base import PRAWBase
from praw.models.reddit.widgets import WidgetEncoder
from praw.reddit import Subreddit

from ... import UnitTest


class TestWidgetEncoder(UnitTest):
    def test_bad_encode(self, reddit):
        data = [
            1,
            "two",
            SubredditWidgetsModeration(reddit.subreddit("subreddit"), reddit),
        ]
        with raises(TypeError):
            dumps(data, cls=WidgetEncoder)  # should throw TypeError

    def test_good_encode(self, reddit):
        data = [
            1,
            "two",
            PRAWBase(reddit, _data={"_secret": "no", "3": 3}),
            reddit.subreddit("four"),
        ]
        assert '[1, "two", {"3": 3}, "four"]' == dumps(data, cls=WidgetEncoder)


class TestWidgets(UnitTest):
    def test_bad_attribute(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        widgets = subreddit.widgets
        widgets._fetched = True
        with pytest.raises(AttributeError):
            _ = widgets.nonexistant_attribute

    def test_repr(self, reddit):
        widgets = SubredditWidgets(
            Subreddit(reddit, pytest.placeholders.test_subreddit)
        )
        assert (
            f"SubredditWidgets(subreddit=Subreddit(display_name={pytest.placeholders.test_subreddit!r}))"
            == repr(widgets)
        )

    def test_subreddit_widgets_mod(self, reddit):
        widgets = SubredditWidgets(
            Subreddit(reddit, pytest.placeholders.test_subreddit)
        )
        assert isinstance(widgets.mod, SubredditWidgetsModeration)

    def test_widget_mod(self, reddit):
        widget = Widget(reddit, {})
        assert isinstance(widget.mod, WidgetModeration)
        assert widget.mod.widget == widget
