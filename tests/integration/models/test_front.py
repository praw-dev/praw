"""Test praw.models.front."""
from .. import IntegrationTest


class TestFront(IntegrationTest):
    def test_controversial(self):
        with self.recorder.use_cassette('TestFront.test_controversial'):
            submissions = list(self.reddit.front.controversial())
        assert len(submissions) == 100

    def test_gilded(self):
        with self.recorder.use_cassette('TestFront.test_gilded'):
            submissions = list(self.reddit.front.gilded())
        assert len(submissions) == 100

    def test_hot(self):
        with self.recorder.use_cassette('TestFront.test_hot'):
            submissions = list(self.reddit.front.hot())
        assert len(submissions) == 100

    def test_new(self):
        with self.recorder.use_cassette('TestFront.test_new'):
            submissions = list(self.reddit.front.new())
        assert len(submissions) == 100

    def test_top(self):
        with self.recorder.use_cassette('TestFront.test_top'):
            submissions = list(self.reddit.front.top())
        assert len(submissions) == 100
