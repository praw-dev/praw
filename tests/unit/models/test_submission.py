
from praw.models import Submission, Redditor, Subreddit

from .. import UnitTest


class TestSubmission(UnitTest):
    def test_objectify_acknowledged(self):
        data = {
            'author': 'dummy_author',
            'subreddit': 'dummy_subreddit'
        }
        Submission._objectify_acknowledged(self.reddit, data=data)

        redditor = data.pop('author')
        assert type(redditor) is Redditor
        assert redditor.name == redditor.a.name == 'dummy_author'
        subreddit = data.pop('subreddit')
        assert type(subreddit) is Subreddit
        assert subreddit.display_name \
            == subreddit.a.display_name == 'dummy_subreddit'
        assert data == {}

        #
        redditor._reddit = None
        subreddit._reddit = None
        data = {
            'author': redditor,
            'subreddit': subreddit
        }
        Submission._objectify_acknowledged(self.reddit, data=data)

        item = data.pop('author')
        assert type(item) is Redditor
        assert redditor.name == redditor.a.name == 'dummy_author'
        assert item._reddit is self.reddit
        item = data.pop('subreddit')
        assert type(item) is Subreddit
        assert subreddit.display_name \
            == subreddit.a.display_name == 'dummy_subreddit'
        assert item._reddit is self.reddit
        assert data == {}

        #
        data = {'author': '[deleted]'}
        Submission._objectify_acknowledged(self.reddit, data=data)

        item = data.pop('author')
        assert item is None

        #
        data = {'author': '[removed]'}
        Submission._objectify_acknowledged(self.reddit, data=data)

        item = data.pop('author')
        assert item is None
