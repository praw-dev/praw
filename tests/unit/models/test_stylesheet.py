"""Test praw.models.Stylesheet."""
from praw.models.stylesheet import Stylesheet

from .. import UnitTest


class TestStylesheet(UnitTest):
    def test_equality(self):
        assert Stylesheet(self.reddit, None) != 5

    def test_repr(self):
        stylesheet = Stylesheet(
            self.reddit, {"images": ["fakeimg"], "stylesheet": "color: blue"}
        )
        assert (
            repr(stylesheet) == "<Stylesheet with 11 characters and 1 images>"
        )
