import pytest
import mock

from ... import IntegrationTest


class TestEmoji(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_remove(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestEmojiModeration.test_remove'):
            subreddit.emoji['test_png'].remove()
            subreddit.emoji['test_jpg'].remove()
