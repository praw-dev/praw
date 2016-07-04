"""Test praw.models.redditor."""
import mock
import pytest
from prawcore import Forbidden

from ... import IntegrationTest


class TestRedditor(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_message(self, _mock_sleep):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestRedditor.test_message'):
            redditor = self.reddit.redditor('subreddit_stats')
            redditor.message('PRAW test', 'This is a test from PRAW')

    @mock.patch('time.sleep', return_value=None)
    def test_message_from_subreddit(self, _mock_sleep):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditor.test_message_from_subreddit'):
            redditor = self.reddit.redditor('subreddit_stats')
            redditor.message('PRAW test', 'This is a test from PRAW',
                             from_subreddit=pytest.placeholders.test_subreddit)


class TestRedditorListings(IntegrationTest):
    def test_comments__controversial(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_comments__controversial'):
            redditor = self.reddit.redditor('spez')
            comments = list(redditor.comments.controversial())
        assert len(comments) == 100

    def test_comments__hot(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_comments__hot'):
            redditor = self.reddit.redditor('spez')
            comments = list(redditor.comments.hot())
        assert len(comments) == 100

    def test_comments__new(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_comments__new'):
            redditor = self.reddit.redditor('spez')
            comments = list(redditor.comments.new())
        assert len(comments) == 100

    def test_comments__top(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_comments__top'):
            redditor = self.reddit.redditor('spez')
            comments = list(redditor.comments.top())
        assert len(comments) == 100

    def test_controversial(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_controversial'):
            redditor = self.reddit.redditor('spez')
            submissions = list(redditor.controversial())
        assert len(submissions) == 100

    def test_downvoted(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_downvoted'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            submissions = list(redditor.downvoted())
        assert len(submissions) > 0

    def test_downvoted__in_read_only_mode(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_downvoted__in_read_only_mode'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            with pytest.raises(Forbidden):
                list(redditor.downvoted())

    def test_downvoted__other_user(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_downvoted__other_user'):
            redditor = self.reddit.redditor('spez')
            with pytest.raises(Forbidden):
                list(redditor.downvoted())

    def test_gilded(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_gilded'):
            redditor = self.reddit.redditor('spez')
            submissions = list(redditor.gilded(limit=50))
        assert len(submissions) == 50

    def test_gildings(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_gildings'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            submissions = list(redditor.gildings())
        assert isinstance(submissions, list)

    def test_gildings__in_read_only_mode(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_gildings__in_read_only_mode'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            with pytest.raises(Forbidden):
                list(redditor.gildings())

    def test_gildings__other_user(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_gildings__other_user'):
            redditor = self.reddit.redditor('spez')
            with pytest.raises(Forbidden):
                list(redditor.gildings())

    def test_hidden(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_hidden'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            submissions = list(redditor.hidden())
        assert len(submissions) > 0

    def test_hidden__in_read_only_mode(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_hidden__in_read_only_mode'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            with pytest.raises(Forbidden):
                list(redditor.hidden())

    def test_hidden__other_user(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_hidden__other_user'):
            redditor = self.reddit.redditor('spez')
            with pytest.raises(Forbidden):
                list(redditor.hidden())

    def test_hot(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_hot'):
            redditor = self.reddit.redditor('spez')
            submissions = list(redditor.hot())
        assert len(submissions) == 100

    def test_new(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_new'):
            redditor = self.reddit.redditor('spez')
            submissions = list(redditor.new())
        assert len(submissions) == 100

    def test_saved(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_saved'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            submissions = list(redditor.saved())
        assert len(submissions) > 0

    def test_saved__in_read_only_mode(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_saved__in_read_only_mode'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            with pytest.raises(Forbidden):
                list(redditor.saved())

    def test_saved__other_user(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_saved__other_user'):
            redditor = self.reddit.redditor('spez')
            with pytest.raises(Forbidden):
                list(redditor.saved())

    def test_submissions__controversial(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_submissions__controversial'):
            redditor = self.reddit.redditor('spladug')
            submissions = list(redditor.submissions.controversial())
        assert len(submissions) == 100

    def test_submissions__hot(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_submissions__hot'):
            redditor = self.reddit.redditor('spez')
            submissions = list(redditor.submissions.hot())
        assert len(submissions) == 100

    def test_submissions__new(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_submissions__new'):
            redditor = self.reddit.redditor('spez')
            submissions = list(redditor.submissions.new())
        assert len(submissions) == 100

    def test_submissions__top(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_submissions__top'):
            redditor = self.reddit.redditor('spladug')
            submissions = list(redditor.submissions.top())
        assert len(submissions) == 100

    def test_top(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_top'):
            redditor = self.reddit.redditor('spez')
            submissions = list(redditor.top())
        assert len(submissions) == 100

    def test_upvoted(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_upvoted'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            submissions = list(redditor.upvoted())
        assert len(submissions) > 0

    def test_upvoted__in_read_only_mode(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_upvoted__in_read_only_mode'):
            redditor = self.reddit.redditor(self.reddit.config.username)
            with pytest.raises(Forbidden):
                list(redditor.upvoted())

    def test_upvoted__other_user(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestRedditorListings.test_upvoted__other_user'):
            redditor = self.reddit.redditor('spez')
            with pytest.raises(Forbidden):
                list(redditor.upvoted())
