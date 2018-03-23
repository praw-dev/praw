from praw.models import Redditor, Emoji
from prawcore import NotFound
import mock
import pytest

from ... import IntegrationTest

class TestEmojiModeration(IntegrationTest):
    def test_add(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        page = Emoji(self.reddit, subreddit, 'test')

        self.reddit.read_only = False
        with self.recorder.use_cassette('TestEmojiModeration.test_add'):
            subreddit.emoji['test'].add('tests/integration/files/test.png')

    def test_remove(self):
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        page = Emoji(self.reddit, subreddit, 'test')

        self.reddit.read_only = False
        with self.recorder.use_cassette('TestEmojiModeration.test_remove'):
            subreddit.emoji['test'].remove()
