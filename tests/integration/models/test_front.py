"""Test praw.models.front."""

from .. import IntegrationTest


class TestFront(IntegrationTest):
    def test_best(self, reddit):
        submissions = list(reddit.front.best())
        assert len(submissions) == 100

    def test_controversial(self, reddit):
        submissions = list(reddit.front.controversial())
        assert len(submissions) == 100

    def test_gilded(self, reddit):
        submissions = list(reddit.front.gilded())
        assert len(submissions) == 100

    def test_hot(self, reddit):
        submissions = list(reddit.front.hot())
        assert len(submissions) == 100

    def test_new(self, reddit):
        submissions = list(reddit.front.new())
        assert len(submissions) == 100

    def test_top(self, reddit):
        submissions = list(reddit.front.top())
        assert len(submissions) == 100
