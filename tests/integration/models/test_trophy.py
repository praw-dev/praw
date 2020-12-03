"""Test praw.models.Trophy"""
from unittest import mock

from .. import IntegrationTest


class TestTrophy(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_equality(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            user = self.reddit.user.me()
            trophies = user.trophies()
            trophies2 = user.trophies()
            assert trophies == trophies2
