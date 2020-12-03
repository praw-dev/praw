"""Test praw.models.subreddits."""
from unittest import mock

from praw.models import Subreddit

from .. import IntegrationTest


class TestSubreddits(IntegrationTest):
    def test_default(self):
        with self.use_cassette():
            subreddits = list(self.reddit.subreddits.default(limit=None))
        assert 0 < len(subreddits) < 100

    def test_premium__without_premium(self):
        with self.use_cassette():
            subreddits = list(self.reddit.subreddits.premium())
        assert len(subreddits) == 0

    def test_premium__with_premium(self):
        with self.use_cassette():
            subreddits = list(self.reddit.subreddits.premium())
        assert len(subreddits) == 100

    def test_gold__without_gold(self):  # ensure backwards compatibility
        with self.use_cassette("TestSubreddits.test_premium__without_premium"):
            subreddits = list(self.reddit.subreddits.gold())
        assert len(subreddits) == 0

    def test_gold__with_gold(self):  # ensure backwards compatibility
        with self.recorder.use_cassette("TestSubreddits.test_premium__with_premium"):
            subreddits = list(self.reddit.subreddits.gold())
        assert len(subreddits) == 100

    def test_new(self):
        with self.use_cassette():
            subreddits = list(self.reddit.subreddits.new(limit=300))
        assert len(subreddits) == 300

    def test_popular(self):
        with self.use_cassette():
            subreddits = list(self.reddit.subreddits.popular(limit=15))
        assert len(subreddits) == 15

    def test_recommended(self):
        with self.use_cassette():
            subreddits = self.reddit.subreddits.recommended(
                ["earthporn"], omit_subreddits=["cityporn"]
            )
        assert len(subreddits) > 1
        for subreddit in subreddits:
            assert isinstance(subreddit, Subreddit)

    def test_recommended__with_multiple(self):
        with self.use_cassette():
            subreddits = self.reddit.subreddits.recommended(
                ["cityporn", "earthporn"],
                omit_subreddits=["skyporn", "winterporn"],
            )
        assert len(subreddits) > 1
        for subreddit in subreddits:
            assert isinstance(subreddit, Subreddit)

    def test_search(self):
        with self.use_cassette():
            found = False
            for subreddit in self.reddit.subreddits.search("praw"):
                assert isinstance(subreddit, Subreddit)
                found = True
            assert found

    def test_search_by_name(self):
        with self.use_cassette():
            subreddits = self.reddit.subreddits.search_by_name("reddit")
            assert isinstance(subreddits, list)
            assert len(subreddits) > 1
            assert all(isinstance(x, Subreddit) for x in subreddits)

    def test_search_by_topic(self):
        with self.use_cassette():
            subreddits = self.reddit.subreddits.search_by_topic("python")
            assert isinstance(subreddits, list)
            assert len(subreddits) > 1
            assert all(isinstance(x, Subreddit) for x in subreddits)

            subreddits = self.reddit.subreddits.search_by_topic("xvfx2741r")
            assert isinstance(subreddits, list)
            assert len(subreddits) == 0

    @mock.patch("time.sleep", return_value=None)
    def test_stream(self, _):
        with self.use_cassette():
            generator = self.reddit.subreddits.stream()
            for i in range(101):
                assert isinstance(next(generator), Subreddit)
