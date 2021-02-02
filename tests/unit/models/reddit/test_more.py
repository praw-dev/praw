import pickle

from praw.models import MoreComments

from ... import UnitTest


class TestComment(UnitTest):
    def test_pickle(self):
        more = MoreComments(self.reddit, {"children": ["a", "b"], "count": 4})
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(more, protocol=level))
            assert more == other

    def test_repr(self):
        more = MoreComments(
            self.reddit, {"children": ["a", "b", "c", "d", "e"], "count": 5}
        )
        assert repr(more) == "<MoreComments count=5, children=['a', 'b', 'c', '...']>"

        more = MoreComments(self.reddit, {"children": ["a", "b", "c", "d"], "count": 4})
        assert repr(more) == "<MoreComments count=4, children=['a', 'b', 'c', 'd']>"

    def test_equality(self):
        more = MoreComments(self.reddit, {"children": ["a", "b", "c", "d"], "count": 4})
        more2 = MoreComments(
            self.reddit, {"children": ["a", "b", "c", "d"], "count": 4}
        )
        assert more == more2
        assert more != 5
