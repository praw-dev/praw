from praw.models import Emoji
import pytest

from ... import IntegrationTest


class TestEmojiModeration(IntegrationTest):
    def test_add(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        emoji = Emoji(self.reddit, subreddit, 'test')

        self.reddit.read_only = False
        with self.recorder.use_cassette('TestEmojiModeration.test_add'):
            emoji.add('tests/integration/files/test.png')

    def test_remove(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        emoji = Emoji(self.reddit, subreddit, 'test')

        self.reddit.read_only = False
        with self.recorder.use_cassette('TestEmojiModeration.test_remove'):
            emoji.remove()
