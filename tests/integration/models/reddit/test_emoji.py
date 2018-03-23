from praw.models import Emoji
import pytest
import mock
from ... import IntegrationTest


class TestEmojiModeration(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_add(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        emoji_png = Emoji(self.reddit, subreddit, 'test_png')
        emoji_jpg = Emoji(self.reddit, subreddit, 'test_jpg')
        with self.recorder.use_cassette('TestEmojiModeration.test_add'):
            emoji_png.add('tests/integration/files/test.png')
            emoji_jpg.add('tests/integration/files/test.jpg')

    @mock.patch('time.sleep', return_value=None)
    def test_remove(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        emoji_png = Emoji(self.reddit, subreddit, 'test_png')
        emoji_jpg = Emoji(self.reddit, subreddit, 'test_jpg')
        with self.recorder.use_cassette('TestEmojiModeration.test_remove'):
            emoji_png.remove()
            emoji_jpg.remove()
