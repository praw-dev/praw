"""Test praw.models.subreddits."""
from praw.models import Subreddit

from .. import IntegrationTest


class TestSubreddits(IntegrationTest):
    def test_default(self):
        with self.recorder.use_cassette('TestSubreddits.test_default'):
            subreddits = list(self.reddit.subreddits.default(limit=None))
        assert 0 < len(subreddits) < 100

    def test_gold__without_gold(self):
        with self.recorder.use_cassette(
                'TestSubreddits.test_gold__without_gold'):
            subreddits = list(self.reddit.subreddits.gold())
        assert len(subreddits) == 0

    def test_new(self):
        with self.recorder.use_cassette('TestSubreddits.test_new'):
            subreddits = list(self.reddit.subreddits.new(limit=300))
        assert len(subreddits) == 300

    def test_popular(self):
        with self.recorder.use_cassette('TestSubreddits.test_popular'):
            subreddits = list(self.reddit.subreddits.popular())
        assert len(subreddits) == 100

    def test_search(self):
        with self.recorder.use_cassette('TestSubreddits.test_search'):
            found = False
            for subreddit in self.reddit.subreddits.search('praw'):
                assert isinstance(subreddit, Subreddit)
                found = True
            assert found

    def test_search_by_name(self):
        with self.recorder.use_cassette('TestSubreddits.test_search_by_name'):
            subreddits = self.reddit.subreddits.search_by_name('reddit')
            assert isinstance(subreddits, list)
            assert len(subreddits) > 1
            assert all(isinstance(x, Subreddit) for x in subreddits)

    def test_stream(self):
        with self.recorder.use_cassette(
                'TestSubreddits__test_streams'):
            generator = self.reddit.subreddits.stream()
            for i in range(101):
                assert isinstance(next(generator), Subreddit)
