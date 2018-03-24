from praw.models import Emoji, SubredditEmoji
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
            assert isinstance(subreddit.emoji, SubredditEmoji)
            for emoji in subreddit.emoji(use_cached=False):
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
                                           'tests/integration/files/test.png',
                                           use_cached=False)
            assert isinstance(emojipng, Emoji)
            emojijpg = subreddit.emoji['test_jpg']
            emojijpg.add('tests/integration/files/test.jpg')
            assert isinstance(emojijpg, Emoji)
            emojicake = subreddit.emoji.add('cake',
                                            'tests/integration/files/test.jpg')
            assert emojicake is None
            emojirep = subreddit.emoji.add('test_png',
                                           'tests/integration/files/test.png',
                                           force_upload=False)
            assert emojirep is None

    @mock.patch('time.sleep', return_value=None)
    def test__get(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestSubredditEmoji.test__get'):
            emoji = subreddit.emoji['test_png']
            assert isinstance(emoji, Emoji)
            assert 'test_png' == emoji.name
            emoji = subreddit.emoji['test_fake']
            assert emoji.url is None

    @mock.patch('time.sleep', return_value=None)
    def test_remove(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestSubredditEmoji.test_remove'):
            subreddit.emoji.remove('test_png', use_cached=False)
            subreddit.emoji.remove('test_jpg')
            subreddit.emoji.remove('test_fake')
