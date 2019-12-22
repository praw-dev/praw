from json import dumps

from praw.models import (
    SubredditWidgets,
    SubredditWidgetsModeration,
    Widget,
    WidgetModeration,
)
from praw.models.reddit.widgets import WidgetEncoder
from praw.models.base import PRAWBase

import pytest


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
        with pytest.raises(TypeError):
            dumps(data, cls=WidgetEncoder)

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
