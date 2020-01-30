"""Test praw.models.user."""
import mock
import pytest
from prawcore.exceptions import BadRequest

from praw.models import Multireddit, Redditor, Subreddit

from .. import IntegrationTest


class TestUser(IntegrationTest):
    def test_blocked(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestUser.test_blocked"):
            blocked = self.reddit.user.blocked()
        assert len(blocked) > 0
        assert all(isinstance(user, Redditor) for user in blocked)

    def test_contributor_subreddits(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestUser.test_contributor_subreddits"
        ):
            count = 0
            for subreddit in self.reddit.user.contributor_subreddits():
                assert isinstance(subreddit, Subreddit)
                count += 1
            assert count > 0

    def test_friends(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestUser.test_friends"):
            friends = self.reddit.user.friends()
        assert len(friends) > 0
        assert all(isinstance(friend, Redditor) for friend in friends)

    @mock.patch("time.sleep", return_value=None)
    def test_friend_exist(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestUser.test_friend_exist"):
            friend = self.reddit.user.friends(user=self.reddit.user.me())
            assert isinstance(friend, Redditor)

    @mock.patch("time.sleep", return_value=None)
    def test_friend_not_exist(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestUser.test_friend_not_exist"):
            with pytest.raises(BadRequest):
                self.reddit.user.friends(user="fake__user_user_user")

    def test_karma(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestUser.test_karma"):
            karma = self.reddit.user.karma()
        assert isinstance(karma, dict)
        for subreddit in karma:
            assert isinstance(subreddit, Subreddit)
            keys = sorted(karma[subreddit].keys())
            assert ["comment_karma", "link_karma"] == keys

    def test_me(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestUser.test_me"):
            me = self.reddit.user.me()
        assert isinstance(me, Redditor)
        me.praw_is_cached = True
        assert self.reddit.user.me().praw_is_cached

    @mock.patch("time.sleep", return_value=None)
    def test_me__bypass_cache(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestUser.test_me__bypass_cache"):
            me = self.reddit.user.me()
            me.praw_is_cached = True
            assert not hasattr(
                self.reddit.user.me(use_cache=False), "praw_is_cached"
            )

    def test_multireddits(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestUser.test_multireddits"):
            multireddits = self.reddit.user.multireddits()
            assert isinstance(multireddits, list)
            assert multireddits
            assert all(isinstance(x, Multireddit) for x in multireddits)

    def test_subreddits(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestUser.test_subreddits"):
            count = 0
            for subreddit in self.reddit.user.subreddits():
                assert isinstance(subreddit, Subreddit)
                count += 1
            assert count > 0
