"""Test praw.reddit."""
import mock

from praw.models import LiveThread

from . import IntegrationTest


class TestReddit(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_live_create(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestReddit.test_live_create'):
            live = self.reddit.live.create('PRAW Create Test')
            assert isinstance(live, LiveThread)
            assert live.title == 'PRAW Create Test'

    def test_random_subreddit(self):
        names = set()
        with self.recorder.use_cassette(
                'TestReddit.test_random_subreddit'):
            for i in range(3):
                names.add(self.reddit.random_subreddit().display_name)
        assert len(names) == 3

    def test_subreddit_with_randnsfw(self):
        with self.recorder.use_cassette(
                'TestReddit.test_subreddit_with_randnsfw'):
            subreddit = self.reddit.subreddit('randnsfw')
            assert subreddit.display_name != 'randnsfw'
            assert subreddit.over18

    def test_subreddit_with_random(self):
        with self.recorder.use_cassette(
                'TestReddit.test_subreddit_with_random'):
            assert self.reddit.subreddit('random').display_name != 'random'
