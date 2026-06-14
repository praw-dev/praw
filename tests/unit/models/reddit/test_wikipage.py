import pickle

from praw.models import Subreddit, WikiPage

from ... import UnitTest


class TestWikiPage(UnitTest):
    def test_equality(self, reddit):
        page1 = WikiPage(reddit, name="x", subreddit=Subreddit(reddit, "a"))
        page2 = WikiPage(reddit, name="2", subreddit=Subreddit(reddit, "a"))
        page3 = WikiPage(reddit, name="1", subreddit=Subreddit(reddit, "b"))
        page4 = WikiPage(reddit, name="x", subreddit=Subreddit(reddit, "A"))
        page5 = WikiPage(reddit, name="X", subreddit=Subreddit(reddit, "a"))
        assert page1 == page1
        assert page2 == page2
        assert page3 == page3
        assert page1 != page2
        assert page1 != page3
        assert page1 == page4
        assert page1 == page5

    def test_hash(self, reddit):
        page1 = WikiPage(reddit, name="x", subreddit=Subreddit(reddit, "a"))
        page2 = WikiPage(reddit, name="2", subreddit=Subreddit(reddit, "a"))
        page3 = WikiPage(reddit, name="1", subreddit=Subreddit(reddit, "b"))
        page4 = WikiPage(reddit, name="x", subreddit=Subreddit(reddit, "A"))
        page5 = WikiPage(reddit, name="X", subreddit=Subreddit(reddit, "a"))
        assert hash(page1) == hash(page1)
        assert hash(page2) == hash(page2)
        assert hash(page3) == hash(page3)
        assert hash(page1) != hash(page2)
        assert hash(page1) != hash(page3)
        assert hash(page1) == hash(page4)
        assert hash(page1) == hash(page5)

    def test_pickle(self, reddit):
        page = WikiPage(reddit, name="x", subreddit=Subreddit(reddit, "a"))
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(page, protocol=level))
            assert page == other

    def test_repr(self, reddit):
        page = WikiPage(reddit, name="x", subreddit=Subreddit(reddit, "a"))
        assert repr(page) == ("WikiPage(subreddit=Subreddit(display_name='a'), name='x')")

    def test_str(self, reddit):
        page = WikiPage(reddit, name="x", subreddit=Subreddit(reddit, "a"))
        assert str(page) == "a/x"
