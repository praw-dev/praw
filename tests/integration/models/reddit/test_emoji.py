import pytest

from praw.exceptions import ClientException
from praw.models import Emoji

from ... import IntegrationTest


class TestEmoji(IntegrationTest):
    def test__fetch(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        emoji = subreddit.emoji["test_png"]
        assert emoji.created_by.startswith("t2_")

    def test__fetch__invalid_emoji(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        emoji = subreddit.emoji["invalid"]
        emoji2 = subreddit.emoji["Test_png"]
        with pytest.raises(ClientException) as excinfo:
            emoji.url
        assert str(excinfo.value) == (f"r/{subreddit} does not have the emoji invalid")
        with pytest.raises(ClientException) as excinfo2:
            emoji2.url
        assert str(excinfo2.value) == (
            f"r/{subreddit} does not have the emoji Test_png"
        )

    def test_delete(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.emoji["test_png"].delete()

    def test_update(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.emoji["test_png"].update(
            mod_flair_only=False, post_flair_allowed=True, user_flair_allowed=True
        )

    def test_update__with_preexisting_values(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        subreddit.emoji["test_png"].update(mod_flair_only=True)


class TestSubredditEmoji(IntegrationTest):
    def test__iter(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        count = 0
        for emoji in subreddit.emoji:
            assert isinstance(emoji, Emoji)
            count += 1
        assert count > 0

    def test_add(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for extension in ["jpg", "png"]:
            emoji = subreddit.emoji.add(
                name=f"test_{extension}",
                image_path=f"tests/integration/files/test.{extension}",
            )
            assert isinstance(emoji, Emoji)

    def test_add_with_perms(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for extension in ["jpg", "png"]:
            emoji = subreddit.emoji.add(
                name=f"test_{extension}",
                image_path=f"tests/integration/files/test.{extension}",
                mod_flair_only=True,
                post_flair_allowed=True,
                user_flair_allowed=False,
            )
            assert isinstance(emoji, Emoji)
