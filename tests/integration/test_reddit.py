"""Test praw.reddit."""
import mock

from . import IntegrationTest


class TestReddit(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_multireddit_create(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestReddit.test_multireddit_create'):
            multireddit = self.reddit.multireddit_create(
                'PRAW create test', subreddits=['redditdev'])
        assert multireddit.display_name == 'PRAW create test'
        assert multireddit.name == 'praw_create_test'

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
