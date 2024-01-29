"""Test praw.models.preferences."""

from praw.models import Preferences

from .. import UnitTest


class TestPreferences(UnitTest):
    def test_creation(self, reddit):
        prefs_obj = reddit.user.preferences
        assert isinstance(prefs_obj, Preferences)
