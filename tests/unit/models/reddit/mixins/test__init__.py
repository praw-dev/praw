import pytest

from praw.models.reddit.mixins import ThingModerationMixin

from .... import UnitTest


class TestThingModerationMixin(UnitTest):
    def test_must_be_extended(self):
        with pytest.raises(NotImplementedError):
            ThingModerationMixin().send_removal_message("public", "title", "message")
