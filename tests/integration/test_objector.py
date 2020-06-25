"""Test praw.objector."""
import pytest

from praw.exceptions import RedditAPIException

from . import IntegrationTest


class TestObjector(IntegrationTest):
    def test_raise_api_exception(self):
        message = "USER_REQUIRED: 'Please log in to do that.'"
        with self.use_cassette():
            submission = self.reddit.submission("4b536h")
            with pytest.raises(RedditAPIException) as excinfo:
                submission.mod.approve()
            assert excinfo.value.items[0].error_type == "USER_REQUIRED"
            assert str(excinfo.value.items[0]) == message
