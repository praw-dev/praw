import pickle

from praw.models import Subreddit, RemovalReason
from praw.models.reddit.removalreason import SubredditRemovalReasons

from ... import UnitTest


class TestRemovalReason(UnitTest):
    def test_equality(self):
        reason1 = RemovalReason(self.reddit, Subreddit(self.reddit, 'a'),
                                '11qiw1rp2mlqd')
        reason2 = RemovalReason(self.reddit, Subreddit(self.reddit, 'a'),
                                '11qiw1rp2mlqd')
        reason3 = RemovalReason(self.reddit, Subreddit(self.reddit, 'b'),
                                '11qjnfc3wdghj')
        assert reason1 == reason1
        assert reason1 == reason2
        assert reason2 != reason3
        assert reason3 == '11qjnfc3wdghj'
        assert reason2 != '11qjnfc3wdghj'

    def test_hash(self):
        reason1 = RemovalReason(self.reddit, Subreddit(self.reddit, 'a'),
                                '11qiw1rp2mlqd')
        reason2 = RemovalReason(self.reddit, Subreddit(self.reddit, 'a'),
                                '11qiw1rp2mlqd')
        reason3 = RemovalReason(self.reddit, Subreddit(self.reddit, 'b'),
                                '11qjnfc3wdghj')
        assert hash(reason1) == hash(reason1)
        assert hash(reason1) == hash(reason2)
        assert hash(reason2) != hash(reason3)

    def test_pickle(self):
        reason = RemovalReason(self.reddit, Subreddit(self.reddit, 'a'),
                               '11qiw1rp2mlqd')
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(reason, protocol=level))
            assert reason == other

    def test_repr(self):
        reason = RemovalReason(self.reddit, Subreddit(self.reddit, 'a'),
                               '11qiw1rp2mlqd')
        assert repr(reason) == ("RemovalReason(id='11qiw1rp2mlqd')")

    def test_str(self):
        reason = RemovalReason(self.reddit, Subreddit(self.reddit, 'a'),
                               '11qiw1rp2mlqd')
        assert str(reason) == '11qiw1rp2mlqd'


class TestSubredditEmoji(UnitTest):
    def test_repr(self):
        se = SubredditRemovalReasons(subreddit=Subreddit(self.reddit, 'a'))
        assert repr(se)  # assert it has some repr
