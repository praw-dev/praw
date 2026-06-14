import pickle

import pytest

from praw.models import Emoji, Subreddit
from praw.models.reddit.emoji import SubredditEmoji

from ... import UnitTest


class TestEmoji(UnitTest):
    def test__get(self, reddit):
        subreddit = reddit.subreddit("a")
        emoji = subreddit.emoji["a"]
        assert isinstance(emoji, Emoji)

    def test_equality(self, reddit):
        emoji1 = Emoji(reddit, name="x", subreddit=Subreddit(reddit, "a"))
        emoji2 = Emoji(reddit, name="2", subreddit=Subreddit(reddit, "a"))
        emoji3 = Emoji(reddit, name="1", subreddit=Subreddit(reddit, "b"))
        emoji4 = Emoji(reddit, name="x", subreddit=Subreddit(reddit, "A"))
        emoji5 = Emoji(reddit, name="X", subreddit=Subreddit(reddit, "a"))
        emoji6 = Emoji(reddit, name="x", subreddit=Subreddit(reddit, "b"))
        assert emoji1 == emoji1
        assert emoji1 == "x"
        assert emoji2 == emoji2
        assert emoji3 == emoji3
        assert emoji1 != emoji2
        assert emoji1 != emoji3
        assert emoji1 == emoji4
        assert emoji1 != emoji5
        assert emoji1 != emoji6
        assert emoji1 != 5

    def test_hash(self, reddit):
        emoji1 = Emoji(reddit, name="x", subreddit=Subreddit(reddit, "a"))
        emoji2 = Emoji(reddit, name="2", subreddit=Subreddit(reddit, "a"))
        emoji3 = Emoji(reddit, name="1", subreddit=Subreddit(reddit, "b"))
        emoji4 = Emoji(reddit, name="x", subreddit=Subreddit(reddit, "A"))
        emoji5 = Emoji(reddit, name="X", subreddit=Subreddit(reddit, "a"))
        emoji6 = Emoji(reddit, name="x", subreddit=Subreddit(reddit, "b"))
        assert hash(emoji1) == hash(emoji1)
        assert hash(emoji2) == hash(emoji2)
        assert hash(emoji3) == hash(emoji3)
        assert hash(emoji1) != hash(emoji2)
        assert hash(emoji1) != hash(emoji3)
        assert hash(emoji1) == hash(emoji4)
        assert hash(emoji1) != hash(emoji5)
        assert hash(emoji1) != hash(emoji6)

    def test_pickle(self, reddit):
        emoji = Emoji(reddit, name="x", subreddit=Subreddit(reddit, "a"))
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(emoji, protocol=level))
            assert emoji == other

    def test_repr(self, reddit):
        emoji = Emoji(reddit, name="x", subreddit=Subreddit(reddit, "a"))
        assert repr(emoji) == "Emoji(name='x')"

    def test_str(self, reddit):
        emoji = Emoji(reddit, name="x", subreddit=Subreddit(reddit, "a"))
        assert str(emoji) == "x"

    def test_update(self, reddit):
        emoji = Emoji(reddit, name="x", subreddit=Subreddit(reddit, "a"))
        with pytest.raises(TypeError) as excinfo:
            emoji.update()
        assert str(excinfo.value) == "At least one attribute must be provided"


class TestSubredditEmoji(UnitTest):
    def test_repr(self, reddit):
        se = SubredditEmoji(subreddit=Subreddit(reddit, "a"))
        assert repr(se)  # assert it has some repr
