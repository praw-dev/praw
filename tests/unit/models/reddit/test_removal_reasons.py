import pickle

import pytest

from praw.models import RemovalReason
from praw.models.reddit.removal_reasons import SubredditRemovalReasons

from ... import UnitTest


class TestRemovalReason(UnitTest):
    def test_equality(self):
        reason1 = RemovalReason(
            self.reddit, subreddit=self.reddit.subreddit("a"), id="x"
        )
        reason2 = RemovalReason(
            self.reddit, subreddit=self.reddit.subreddit("a"), id="2"
        )
        reason3 = RemovalReason(
            self.reddit, subreddit=self.reddit.subreddit("b"), id="1"
        )
        reason4 = RemovalReason(
            self.reddit, subreddit=self.reddit.subreddit("A"), id="x"
        )
        reason5 = RemovalReason(
            self.reddit, subreddit=self.reddit.subreddit("a"), reason_id="X"
        )
        assert reason1 == reason1
        assert reason1 == "x"
        assert reason2 == reason2
        assert reason3 == reason3
        assert reason1 != reason2
        assert reason1 != reason3
        assert reason1 == reason4
        assert reason1 != reason5

    def test_exception(self):
        with pytest.raises(ValueError):
            RemovalReason(self.reddit, subreddit=self.reddit.subreddit("a"))
        with pytest.raises(ValueError):
            RemovalReason(
                self.reddit,
                subreddit=self.reddit.subreddit("a"),
                id="test",
                _data={},
            )
        with pytest.raises(ValueError):
            RemovalReason(self.reddit, subreddit=self.reddit.subreddit("a"), id="")
        with pytest.raises(ValueError):
            RemovalReason(
                self.reddit, subreddit=self.reddit.subreddit("a"), reason_id=""
            )

    def test__get(self):
        subreddit = self.reddit.subreddit("a")
        removal_reason = subreddit.mod.removal_reasons["a"]
        assert isinstance(removal_reason, RemovalReason)

    def test_hash(self):
        reason1 = RemovalReason(
            self.reddit, subreddit=self.reddit.subreddit("a"), id="x"
        )
        reason2 = RemovalReason(
            self.reddit, subreddit=self.reddit.subreddit("a"), id="2"
        )
        reason3 = RemovalReason(
            self.reddit, subreddit=self.reddit.subreddit("b"), id="1"
        )
        reason4 = RemovalReason(
            self.reddit, subreddit=self.reddit.subreddit("A"), id="x"
        )
        reason5 = RemovalReason(
            self.reddit, subreddit=self.reddit.subreddit("a"), reason_id="X"
        )
        assert hash(reason1) == hash(reason1)
        assert hash(reason2) == hash(reason2)
        assert hash(reason3) == hash(reason3)
        assert hash(reason1) != hash(reason2)
        assert hash(reason1) != hash(reason3)
        assert hash(reason1) == hash(reason4)
        assert hash(reason1) != hash(reason5)

    def test_pickle(self):
        reason = RemovalReason(
            self.reddit, subreddit=self.reddit.subreddit("a"), id="x"
        )
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(reason, protocol=level))
            assert reason == other

    def test_repr(self):
        reason = RemovalReason(
            self.reddit, subreddit=self.reddit.subreddit("a"), id="x"
        )
        assert repr(reason) == "RemovalReason(id='x')"

    def test_str(self):
        reason = RemovalReason(
            self.reddit, subreddit=self.reddit.subreddit("a"), id="x"
        )
        assert str(reason) == "x"


class TestSubredditRemovalReasons(UnitTest):
    def test_repr(self):
        sr = SubredditRemovalReasons(subreddit=self.reddit.subreddit("a"))
        assert repr(sr)  # assert it has some repr
