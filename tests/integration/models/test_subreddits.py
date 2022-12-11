"""Test praw.models.subreddits."""
import pytest

from praw.models import Subreddit

from .. import IntegrationTest


class TestSubreddits(IntegrationTest):
    def test_default(self, reddit):
        subreddits = list(reddit.subreddits.default(limit=None))
        assert 0 < len(subreddits) < 100

    @pytest.mark.cassette_name("TestSubreddits.test_premium__with_premium")
    def test_gold__with_gold(self, reddit):  # ensure backwards compatibility
        subreddits = list(reddit.subreddits.gold())
        assert len(subreddits) == 100

    @pytest.mark.cassette_name("TestSubreddits.test_premium__without_premium")
    def test_gold__without_gold(self, reddit):  # ensure backwards compatibility
        subreddits = list(reddit.subreddits.gold())
        assert len(subreddits) == 0

    def test_new(self, reddit):
        subreddits = list(reddit.subreddits.new(limit=300))
        assert len(subreddits) == 300

    def test_popular(self, reddit):
        subreddits = list(reddit.subreddits.popular(limit=15))
        assert len(subreddits) == 15

    def test_premium__with_premium(self, reddit):
        subreddits = list(reddit.subreddits.premium())
        assert len(subreddits) == 100

    def test_premium__without_premium(self, reddit):
        subreddits = list(reddit.subreddits.premium())
        assert len(subreddits) == 0

    def test_recommended(self, reddit):
        subreddits = reddit.subreddits.recommended(
            ["earthporn"], omit_subreddits=["cityporn"]
        )
        assert len(subreddits) > 1
        for subreddit in subreddits:
            assert isinstance(subreddit, Subreddit)

    def test_recommended__with_multiple(self, reddit):
        subreddits = reddit.subreddits.recommended(
            ["cityporn", "earthporn"],
            omit_subreddits=["skyporn", "winterporn"],
        )
        assert len(subreddits) > 1
        for subreddit in subreddits:
            assert isinstance(subreddit, Subreddit)

    def test_search(self, reddit):
        found = False
        for subreddit in reddit.subreddits.search("praw"):
            assert isinstance(subreddit, Subreddit)
            found = True
        assert found

    def test_search_by_name(self, reddit):
        subreddits = reddit.subreddits.search_by_name("praw.reddit.Reddit")
        assert isinstance(subreddits, list)
        assert len(subreddits) > 1
        assert all(isinstance(x, Subreddit) for x in subreddits)

    def test_search_by_topic(self, reddit):
        subreddits = reddit.subreddits.search_by_topic("python")
        assert isinstance(subreddits, list)
        assert len(subreddits) > 1
        assert all(isinstance(x, Subreddit) for x in subreddits)

        subreddits = reddit.subreddits.search_by_topic("xvfx2741r")
        assert isinstance(subreddits, list)
        assert len(subreddits) == 0

    def test_stream(self, reddit):
        generator = reddit.subreddits.stream()
        for i in range(101):
            assert isinstance(next(generator), Subreddit)
