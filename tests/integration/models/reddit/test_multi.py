from praw.models import Subreddit
import mock

from ... import IntegrationTest


class TestMultireddit(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_add(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestMulireddit.test_add'):
            multi = self.reddit.user.multireddits()[0]
            multi.add('redditdev')

    @mock.patch('time.sleep', return_value=None)
    def test_remove(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestMulireddit.test_remove'):
            multi = self.reddit.user.multireddits()[0]
            multi.remove('redditdev')

    def test_subreddits(self):
        multi = self.reddit.multireddit('kjoneslol', 'sfwpornnetwork')
        with self.recorder.use_cassette('TestMulireddit.test_subreddits'):
            assert multi.subreddits
        assert all(isinstance(x, Subreddit) for x in multi.subreddits)
