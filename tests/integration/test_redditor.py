"""Test praw.models.front."""
from . import IntegrationTest


class TestRedditorListings(IntegrationTest):
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
            submissions = list(redditor.gilded(limit=50))
        assert len(submissions) == 50

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
