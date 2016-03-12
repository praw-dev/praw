"""Test praw.models.mixins.listing."""
import pytest

from .. import UnitTest


class TestMixinListing(UnitTest):
    def test_controversial_raises_value_error(self):
        with pytest.raises(ValueError):
            self.reddit.front.controversial('second')

    def test_top_raises_value_error(self):
        with pytest.raises(ValueError):
            self.reddit.front.top('second')
