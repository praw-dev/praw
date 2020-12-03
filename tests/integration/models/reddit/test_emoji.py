from unittest import mock

import pytest

from praw.exceptions import ClientException
from praw.models import Emoji

from ... import IntegrationTest


class TestEmoji(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test__fetch(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        emoji = subreddit.emoji["test_png"]
        with self.use_cassette():
            assert emoji.created_by.startswith("t2_")

    @mock.patch("time.sleep", return_value=None)
    def test__fetch__invalid_emoji(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        emoji = subreddit.emoji["invalid"]
        emoji2 = subreddit.emoji["Test_png"]
        with self.use_cassette():
            with pytest.raises(ClientException) as excinfo:
                emoji.url
            assert str(excinfo.value) == (
                f"r/{subreddit} does not have the emoji invalid"
            )
            with pytest.raises(ClientException) as excinfo2:
                emoji2.url
            assert str(excinfo2.value) == (
                f"r/{subreddit} does not have the emoji Test_png"
            )

    def test_delete(self):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.use_cassette():
            subreddit.emoji["test_png"].delete()

    @mock.patch("time.sleep", return_value=None)
    def test_update(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.use_cassette():
            subreddit.emoji["test_png"].update(
                mod_flair_only=False,
                post_flair_allowed=True,
                user_flair_allowed=True,
            )

    @mock.patch("time.sleep", return_value=None)
    def test_update__with_preexisting_values(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.use_cassette():
            subreddit.emoji["test_png"].update(mod_flair_only=True)


class TestSubredditEmoji(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test__iter(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.use_cassette():
            count = 0
            for emoji in subreddit.emoji:
                assert isinstance(emoji, Emoji)
                count += 1
            assert count > 0

    @mock.patch("time.sleep", return_value=None)
    def test_add(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.use_cassette():
            for extension in ["jpg", "png"]:
                emoji = subreddit.emoji.add(
                    f"test_{extension}",
                    f"tests/integration/files/test.{extension}",
                )
                assert isinstance(emoji, Emoji)

    @mock.patch("time.sleep", return_value=None)
    def test_add_with_perms(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.use_cassette():
            for extension in ["jpg", "png"]:
                emoji = subreddit.emoji.add(
                    f"test_{extension}",
                    f"tests/integration/files/test.{extension}",
                    mod_flair_only=True,
                    post_flair_allowed=True,
                    user_flair_allowed=False,
                )
                assert isinstance(emoji, Emoji)
