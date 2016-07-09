"""Test praw.models.user."""
from praw.models import Redditor

from .. import IntegrationTest


class TestUser(IntegrationTest):
    def test_blocked(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestUser.test_blocked'):
            blocked = self.reddit.user.blocked()
        assert len(blocked) > 0
        assert all(isinstance(user, Redditor) for user in blocked)

        # Additional assertions for BaseList class
        # These should be moved into a unit test.
        assert str(blocked).startswith('[')
        assert str(blocked).endswith(']')
        assert 'PyAPITestUser3' in blocked
        assert 'PyAPITestUser3' == blocked[1]

    def test_friends(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestUser.test_friends'):
            friends = self.reddit.user.friends()
        assert len(friends) > 0
        assert all(isinstance(friend, Redditor) for friend in friends)

    def test_me(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestUser.test_me'):
            me = self.reddit.user.me()
        assert isinstance(me, Redditor)
