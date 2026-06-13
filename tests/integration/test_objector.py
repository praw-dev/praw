"""Test praw.objector."""

import pytest

from praw.exceptions import RedditAPIException

from . import IntegrationTest


class TestObjector(IntegrationTest):
    def test_objectify__errors_null(self, reddit):
        # Some endpoints (e.g. api/hide) now respond with {"json": {"errors":
        # null}} rather than an empty list. ``objectify`` must treat null like an
        # empty list and not raise (previously ``len(None)`` raised TypeError).
        reddit.read_only = False
        reddit.submission("4b1tfm").hide()

    def test_raise_api_exception(self, reddit):
        message = "USER_REQUIRED: 'Please log in to do that.'"
        submission = reddit.submission("4b536h")
        with pytest.raises(RedditAPIException) as excinfo:
            submission.mod.approve()
        assert excinfo.value.items[0].error_type == "USER_REQUIRED"
        assert str(excinfo.value.items[0]) == message
