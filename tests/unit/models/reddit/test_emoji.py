import pickle

from praw.models import Subreddit, Emoji

from ... import UnitTest


class TestEmoji(UnitTest):
    def test_equality(self):
        emoji1 = Emoji(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                       name='x')
        emoji2 = Emoji(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                       name='2')
        emoji3 = Emoji(self.reddit, subreddit=Subreddit(self.reddit, 'b'),
                       name='1')
        emoji4 = Emoji(self.reddit, subreddit=Subreddit(self.reddit, 'A'),
                       name='x')
        assert emoji1 == emoji1
        assert emoji2 == emoji2
        assert emoji3 == emoji3
        assert emoji1 != emoji2
        assert emoji1 != emoji3
        assert emoji1 == emoji4

    def test_hash(self):
        emoji1 = Emoji(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                       name='x')
        emoji2 = Emoji(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                       name='2')
        emoji3 = Emoji(self.reddit, subreddit=Subreddit(self.reddit, 'b'),
                       name='1')
        emoji4 = Emoji(self.reddit, subreddit=Subreddit(self.reddit, 'A'),
                       name='x')
        assert hash(emoji1) == hash(emoji1)
        assert hash(emoji2) == hash(emoji2)
        assert hash(emoji3) == hash(emoji3)
        assert hash(emoji1) != hash(emoji2)
        assert hash(emoji1) != hash(emoji3)
        assert hash(emoji1) == hash(emoji4)

    def test_pickle(self):
        emoji = Emoji(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                      name='x')
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(emoji, protocol=level))
            assert page == other

    def test_repr(self):
        emoji = Emoji(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                      name='x')
        assert repr(emoji) == ('Emoji(subreddit=Subreddit(display_name=\'a\''
                              '), name=\'x\')')

    def test_str(self):
        emoji = Emoji(self.reddit, subreddit=Subreddit(self.reddit, 'a'),
                      name='x')
        assert str(emoji) == 'a/x'
