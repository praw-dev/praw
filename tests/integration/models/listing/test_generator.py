"""Test praw.models.listing.generator."""

from ... import IntegrationTest


class TestListingGenerator(IntegrationTest):
    def test_exhaust_items(self, reddit):
        submissions = list(reddit.redditor("spez").top(limit=None))
        assert len(submissions) > 100

    def test_exhaust_items_with_before(self, reddit):
        submissions = list(
            reddit.redditor("spez").top(limit=None, params={"before": "3cxedn"})
        )
        assert len(submissions) > 100

    def test_no_items(self, reddit):
        submissions = list(reddit.redditor("spez").top(time_filter="hour"))
        assert len(submissions) == 0
