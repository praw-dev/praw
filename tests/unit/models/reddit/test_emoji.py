import pickle
from unittest import mock

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
        emoji1 = Emoji(reddit, subreddit=Subreddit(reddit, "a"), name="x")
        emoji2 = Emoji(reddit, subreddit=Subreddit(reddit, "a"), name="2")
        emoji3 = Emoji(reddit, subreddit=Subreddit(reddit, "b"), name="1")
        emoji4 = Emoji(reddit, subreddit=Subreddit(reddit, "A"), name="x")
        emoji5 = Emoji(reddit, subreddit=Subreddit(reddit, "a"), name="X")
        emoji6 = Emoji(reddit, subreddit=Subreddit(reddit, "b"), name="x")
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
        emoji1 = Emoji(reddit, subreddit=Subreddit(reddit, "a"), name="x")
        emoji2 = Emoji(reddit, subreddit=Subreddit(reddit, "a"), name="2")
        emoji3 = Emoji(reddit, subreddit=Subreddit(reddit, "b"), name="1")
        emoji4 = Emoji(reddit, subreddit=Subreddit(reddit, "A"), name="x")
        emoji5 = Emoji(reddit, subreddit=Subreddit(reddit, "a"), name="X")
        emoji6 = Emoji(reddit, subreddit=Subreddit(reddit, "b"), name="x")
        assert hash(emoji1) == hash(emoji1)
        assert hash(emoji2) == hash(emoji2)
        assert hash(emoji3) == hash(emoji3)
        assert hash(emoji1) != hash(emoji2)
        assert hash(emoji1) != hash(emoji3)
        assert hash(emoji1) == hash(emoji4)
        assert hash(emoji1) != hash(emoji5)
        assert hash(emoji1) != hash(emoji6)

    def test_pickle(self, reddit):
        emoji = Emoji(reddit, subreddit=Subreddit(reddit, "a"), name="x")
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(emoji, protocol=level))
            assert emoji == other

    def test_repr(self, reddit):
        emoji = Emoji(reddit, subreddit=Subreddit(reddit, "a"), name="x")
        assert repr(emoji) == "Emoji(name='x')"

    def test_str(self, reddit):
        emoji = Emoji(reddit, subreddit=Subreddit(reddit, "a"), name="x")
        assert str(emoji) == "x"

    def test_update(self, reddit):
        emoji = Emoji(reddit, subreddit=Subreddit(reddit, "a"), name="x")
        with pytest.raises(TypeError) as excinfo:
            emoji.update()
        assert str(excinfo.value) == "At least one attribute must be provided"

    @mock.patch("praw.models.reddit.emoji.Path.open", new_callable=mock.mock_open)
    def test_add_emoji_500(self, _mock_open, reddit):
        from prawcore.exceptions import ServerError
        from requests.exceptions import HTTPError

        http_response = mock.Mock()
        http_response.status_code = 500

        response = mock.Mock()
        response.ok = True
        response.raise_for_status = mock.Mock(
            side_effect=HTTPError(response=http_response)
        )

        subreddit = reddit.subreddit("test")

        lease_response = {
            "s3UploadLease": {
                "action": "",
                "fields": [
                    {"name": "key", "value": "value"},
                ],
            }
        }

        post_mock = mock.Mock(side_effect=[lease_response, None])

        with mock.patch.object(subreddit._reddit, "post", post_mock):
            subreddit._reddit._core._requestor._http.post = mock.Mock(return_value=response)
            with pytest.raises(ServerError):
                subreddit.emoji.add(name="emoji", image_path="/dev/null")


class TestSubredditEmoji(UnitTest):
    def test_repr(self, reddit):
        se = SubredditEmoji(subreddit=Subreddit(reddit, "a"))
        assert repr(se)  # assert it has some repr
