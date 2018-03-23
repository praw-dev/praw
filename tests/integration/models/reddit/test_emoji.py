from praw.models import Emoji
import pytest

from ... import IntegrationTest


class TestEmojiModeration(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_add(self, _):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        emoji = Emoji(self.reddit, subreddit, 'test')

        self.reddit.read_only = False
        with self.recorder.use_cassette('TestEmojiModeration.test_add'):
            emoji.add('tests/integration/files/test.png')

    @mock.patch('time.sleep', return_value=None)
    def test_remove(self, _):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        emoji = Emoji(self.reddit, subreddit, 'test')

        self.reddit.read_only = False
        with self.recorder.use_cassette('TestEmojiModeration.test_remove'):
            emoji.remove()
