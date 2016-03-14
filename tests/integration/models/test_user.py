"""Test praw.models.user."""
from praw.models import Redditor

from .. import IntegrationTest


class TestUser(IntegrationTest):
    def test_friends(self):
        with self.recorder.use_cassette('TestUser.test_friends'):
            self.reddit.read_only = False
            friends = self.reddit.user.friends()
        assert len(friends) > 0
        assert all(isinstance(friend, Redditor) for friend in friends)

    def test_me(self):
        with self.recorder.use_cassette('TestUser.test_me'):
            self.reddit.read_only = False
            me = self.reddit.user.me()
        assert isinstance(me, Redditor)
