"""Test praw.models.front."""
import pytest
from betamax import Betamax
from praw import Reddit


class TestRedditorListings(object):
    def setup(self):
        self.reddit = Reddit(client_id=pytest.placeholders.client_id,
                             client_secret=pytest.placeholders.client_secret,
                             user_agent=pytest.placeholders.user_agent)
        self.recorder = Betamax(self.reddit._core._requestor._http)

    def test_controversial(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_controversial'):
            redditor = self.reddit.redditor('spez')
            submissions = list(redditor.controversial())
        assert len(submissions) == 100

    def test_gilded(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_gilded'):
            redditor = self.reddit.redditor('spez')
            submissions = list(redditor.gilded())
        assert len(submissions) >= 50

    """
    def test_gildings(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_gildings'):
            redditor = self.reddit.redditor('pyapitestuser2')
            submissions = list(redditor.gildings())
        assert len(submissions) >= 50

    def test_gildings_fails_on_other(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_gildings_fails_on_other'):
            redditor = self.reddit.redditor('spez')
            submissions = list(redditor.gildings())
        assert len(submissions) >= 50
    """

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

    def test_top(self):
        with self.recorder.use_cassette(
                'TestRedditorListings.test_top'):
            redditor = self.reddit.redditor('spez')
            submissions = list(redditor.top())
        assert len(submissions) == 100
