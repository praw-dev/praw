"""Test praw.models.front."""
import pytest
from betamax import Betamax
from praw import Reddit


class TestListingGenerator(object):
    def setup(self):
        self.reddit = Reddit(client_id=pytest.placeholders.client_id,
                             client_secret=pytest.placeholders.client_secret,
                             user_agent=pytest.placeholders.user_agent)
        self.recorder = Betamax(self.reddit._core._requestor._http)

    def test_exhaust_items(self):
        with self.recorder.use_cassette(
                'TestListingGenerator.test_exhaust_items'):
            submissions = list(self.reddit.redditor('spez').top(limit=None))
        assert len(submissions) > 100

    def test_no_items(self):
        with self.recorder.use_cassette('TestListingGenerator.test_no_items'):
            submissions = list(self.reddit.redditor('spez').top('hour'))
        assert len(submissions) == 0
