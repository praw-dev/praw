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
            assert 'redditdev' in multi.subreddits

    @mock.patch('time.sleep', return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestMulireddit.test_delete'):
            multi = self.reddit.user.multireddits()[0]
            multi.delete()

    @mock.patch('time.sleep', return_value=None)
    def test_remove(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestMulireddit.test_remove'):
            multi = self.reddit.user.multireddits()[0]
            multi.remove('redditdev')
            assert 'redditdev' not in multi.subreddits

    @mock.patch('time.sleep', return_value=None)
    def test_rename(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestMulireddit.test_rename'):
            multi = self.reddit.user.multireddits()[0]
            multi.rename('PRAW Renamed')
            assert multi.display_name == 'PRAW Renamed'
            assert multi.name == 'praw_renamed'

    def test_subreddits(self):
        multi = self.reddit.multireddit('kjoneslol', 'sfwpornnetwork')
        with self.recorder.use_cassette('TestMulireddit.test_subreddits'):
            assert multi.subreddits
        assert all(isinstance(x, Subreddit) for x in multi.subreddits)
