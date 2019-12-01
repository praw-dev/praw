import pickle

from praw.models import Subreddit, Reason
from praw.models.reddit.reasons import SubredditReasons

from ... import UnitTest


class TestReason(UnitTest):
    def test_equality(self):
        reason1 = Reason(
            self.reddit, subreddit=Subreddit(self.reddit, "a"), reason_id="x"
        )
        reason2 = Reason(
            self.reddit, subreddit=Subreddit(self.reddit, "a"), reason_id="2"
        )
        reason3 = Reason(
            self.reddit, subreddit=Subreddit(self.reddit, "b"), reason_id="1"
        )
        reason4 = Reason(
            self.reddit, subreddit=Subreddit(self.reddit, "A"), reason_id="x"
        )
        reason5 = Reason(
            self.reddit, subreddit=Subreddit(self.reddit, "a"), reason_id="X"
        )
        reason6 = Reason(
            self.reddit, subreddit=Subreddit(self.reddit, "b"), reason_id="x"
        )
        assert reason1 == reason1
        assert reason1 == "x"
        assert reason2 == reason2
        assert reason3 == reason3
        assert reason1 != reason2
        assert reason1 != reason3
        assert reason1 == reason4
        assert reason1 != reason5
        assert reason1 != reason6

    def test__get(self):
        subreddit = self.reddit.subreddit("a")
        reason = subreddit.reasons["a"]
        assert isinstance(reason, Reason)

    def test_hash(self):
        reason1 = Reason(
            self.reddit, subreddit=Subreddit(self.reddit, "a"), reason_id="x"
        )
        reason2 = Reason(
            self.reddit, subreddit=Subreddit(self.reddit, "a"), reason_id="2"
        )
        reason3 = Reason(
            self.reddit, subreddit=Subreddit(self.reddit, "b"), reason_id="1"
        )
        reason4 = Reason(
            self.reddit, subreddit=Subreddit(self.reddit, "A"), reason_id="x"
        )
        reason5 = Reason(
            self.reddit, subreddit=Subreddit(self.reddit, "a"), reason_id="X"
        )
        reason6 = Reason(
            self.reddit, subreddit=Subreddit(self.reddit, "b"), reason_id="x"
        )
        assert hash(reason1) == hash(reason1)
        assert hash(reason2) == hash(reason2)
        assert hash(reason3) == hash(reason3)
        assert hash(reason1) != hash(reason2)
        assert hash(reason1) != hash(reason3)
        assert hash(reason1) == hash(reason4)
        assert hash(reason1) != hash(reason5)
        assert hash(reason1) != hash(reason6)

    def test_pickle(self):
        reason = Reason(
            self.reddit, subreddit=Subreddit(self.reddit, "a"), reason_id="x"
        )
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(reason, protocol=level))
            assert reason == other

    def test_repr(self):
        reason = Reason(
            self.reddit, subreddit=Subreddit(self.reddit, "a"), reason_id="x"
        )
        assert repr(reason) == ("Reason(id='x')")

    def test_str(self):
        reason = Reason(
            self.reddit, subreddit=Subreddit(self.reddit, "a"), reason_id="x"
        )
        assert str(reason) == "x"


class TestSubredditReasons(UnitTest):
    def test_repr(self):
        sr = SubredditReasons(subreddit=Subreddit(self.reddit, "a"))
        assert repr(sr)  # assert it has some repr
