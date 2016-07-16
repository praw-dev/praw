import pickle

from praw.models import Subreddit, WikiPage

from ... import UnitTest


class TestWikiPage(UnitTest):
    def test_equality(self):
        page1 = WikiPage(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                         name='x')
        page2 = WikiPage(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                         name='2')
        page3 = WikiPage(self.reddit, subreddit=Subreddit(self.reddit, 'b'),
                         name='1')
        page4 = WikiPage(self.reddit, subreddit=Subreddit(self.reddit, 'A'),
                         name='x')
        page5 = WikiPage(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                         name='X')
        assert page1 == page1
        assert page2 == page2
        assert page3 == page3
        assert page1 != page2
        assert page1 != page3
        assert page1 == page4
        assert page1 == page5

    def test_hash(self):
        page1 = WikiPage(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                         name='x')
        page2 = WikiPage(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                         name='2')
        page3 = WikiPage(self.reddit, subreddit=Subreddit(self.reddit, 'b'),
                         name='1')
        page4 = WikiPage(self.reddit, subreddit=Subreddit(self.reddit, 'A'),
                         name='x')
        page5 = WikiPage(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                         name='X')
        assert hash(page1) == hash(page1)
        assert hash(page2) == hash(page2)
        assert hash(page3) == hash(page3)
        assert hash(page1) != hash(page2)
        assert hash(page1) != hash(page3)
        assert hash(page1) == hash(page4)
        assert hash(page1) == hash(page5)

    def test_pickle(self):
        page = WikiPage(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                        name='x')
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(page, protocol=level))
            assert page == other

    def test_repr(self):
        page = WikiPage(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                        name='x')
        assert repr(page) == ('WikiPage(subreddit=Subreddit(display_name=\'a\''
                              '), name=\'x\')')

    def test_str(self):
        page = WikiPage(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                        name='x')
        assert str(page) == 'a/x'
