from praw.exceptions import ClientException
from praw.models import Emoji
import mock
import pytest

from ... import IntegrationTest


class TestEmoji(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test__fetch(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        emoji = subreddit.emoji["test_png"]
        with self.recorder.use_cassette("TestEmoji.test__fetch"):
            assert emoji.created_by.startswith("t2_")

    @mock.patch("time.sleep", return_value=None)
    def test__fetch__invalid_emoji(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        emoji = subreddit.emoji["invalid"]
        emoji2 = subreddit.emoji["Test_png"]
        with self.recorder.use_cassette(
            "TestEmoji.test__fetch__invalid_emoji"
        ):
            with pytest.raises(ClientException) as excinfo:
                emoji.url
            assert str(excinfo.value) == (
                "/r/{} does not have the emoji {}".format(subreddit, "invalid")
            )
            with pytest.raises(ClientException) as excinfo2:
                emoji2.url
            assert str(excinfo2.value) == (
                "r/{} does not have the emoji {}".format(
                    subreddit, "Test_png"
                )
            )

    def test_delete(self):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette("TestEmoji.test_delete"):
            subreddit.emoji["test_png"].delete()


class TestSubredditEmoji(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test__iter(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette("TestSubredditEmoji.test__iter"):
            count = 0
            for emoji in subreddit.emoji:
                assert isinstance(emoji, Emoji)
                count += 1
            assert count > 0

    @mock.patch("time.sleep", return_value=None)
    def test_add(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette("TestSubredditEmoji.test_add"):
            for extension in ["jpg", "png"]:
                emoji = subreddit.emoji.add(
                    "test_{}".format(extension),
                    "tests/integration/files/test.{}".format(extension),
                )
                assert isinstance(emoji, Emoji)
