from praw.models import Subreddit

from ... import IntegrationTest


class TestMultireddit(IntegrationTest):
    def test_subreddits(self):
        multi = self.reddit.multireddit('kjoneslol', 'sfwpornnetwork')
        with self.recorder.use_cassette('TestMulireddit.test_subreddits'):
            assert multi.subreddits
        assert all(isinstance(x, Subreddit) for x in multi.subreddits)
