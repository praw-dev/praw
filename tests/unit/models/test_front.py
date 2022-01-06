"""Test praw.models.front."""
import pytest

from .. import UnitTest


class TestFront(UnitTest):
    def test_controversial_raises_value_error(self):
        with pytest.raises(ValueError):
            self.reddit.front.controversial(time_filter="second")

    def test_top_raises_value_error(self):
        with pytest.raises(ValueError):
            self.reddit.front.top(time_filter="second")
