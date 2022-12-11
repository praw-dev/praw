"""Test praw.models.Trophy"""

from .. import IntegrationTest


class TestTrophy(IntegrationTest):
    def test_equality(self, reddit):
        reddit.read_only = False
        user = reddit.user.me()
        trophies = user.trophies()
        trophies2 = user.trophies()
        assert trophies == trophies2
