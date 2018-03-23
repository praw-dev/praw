from praw.models import Emoji, SubredditEmoji
from prawcore import NotFound
import mock
import pytest

from ... import IntegrationTest


class TestSubredditEmoji(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test__call(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestSubredditEmoji.test__call'):
            count = 0
            for emoji in subreddit.emoji():
                assert isinstance(emoji, Emoji)
                count += 1
            assert count > 0

    @mock.patch('time.sleep', return_value=None)
    def test_add(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestSubredditEmoji.test_add'):
            emojipng = subreddit.emoji.add('test_png',
                                           'tests/integration/files/test.png')
            assert isinstance(emojipng, Emoji)
            emojijpg = subreddit.emoji.add('test_jpg',
                                           'tests/integration/files/test.jpg')
            assert isinstance(emojijpg, Emoji)

    @mock.patch('time.sleep', return_value=None)
    def test__get(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestSubredditEmoji.test__get'):
            emoji = subreddit.emoji['test_png']
            assert isinstance(emoji, Emoji)
            assert 'test_png' == emoji.name

    @mock.patch('time.sleep', return_value=None)
    def test_remove(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestSubredditEmoji.test_remove'):
            subreddit.emoji.remove('test_png')
            subreddit.emoji.remove('test_jpg')
            subreddit.emoji.remove('test_fake')
