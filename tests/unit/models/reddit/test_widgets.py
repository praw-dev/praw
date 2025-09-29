from json import dumps
from unittest import mock

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
        assert dumps(data, cls=WidgetEncoder) == '[1, "two", {"3": 3}, "four"]'


class TestWidget(UnitTest):
    def test_equality(self):
        widget1 = Widget(None, {"id": "a"})
        widget2 = Widget(None, {"id": "b"})
        widget3 = Widget(None, {"id": "A"})
        assert widget1 == widget1
        assert widget1 != widget2
        assert widget1 == widget3

    def test_hash(self):
        widget1 = Widget(None, {"id": "a"})
        widget2 = Widget(None, {"id": "b"})
        widget3 = Widget(None, {"id": "A"})
        assert hash(widget1) == hash(widget1)
        assert hash(widget1) != hash(widget2)
        assert hash(widget1) == hash(widget3)


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


class TestSubredditWidgetsModeration(UnitTest):
    @mock.patch("praw.models.reddit.widgets.Path.open", new_callable=mock.mock_open)
    def test_upload_image_500(self, _mock_open, reddit):
        from prawcore.exceptions import ServerError
        from requests.exceptions import HTTPError

        http_response = mock.Mock()
        http_response.status_code = 500

        response = mock.Mock()
        response.ok = True
        response.raise_for_status = mock.Mock(
            side_effect=HTTPError(response=http_response)
        )

        subreddit = reddit.subreddit("test")
        widgets_mod = subreddit.widgets.mod

        lease_response = {
            "s3UploadLease": {
                "action": "",
                "fields": [
                    {"name": "key", "value": "value"},
                ],
            }
        }

        with mock.patch.object(widgets_mod._reddit, "post", return_value=lease_response):
            widgets_mod._reddit._core._requestor._http.post = mock.Mock(return_value=response)
            with pytest.raises(ServerError):
                widgets_mod.upload_image("/dev/null")
