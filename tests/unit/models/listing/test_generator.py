"""Test praw.models.front."""
from praw.models.listing.generator import ListingGenerator

from ... import UnitTest


class TestListingGenerator(UnitTest):
    def test_params_are_not_modified(self):
        params = {'prawtest': 'yes'}
        generator = ListingGenerator(None, None, params=params)
        assert 'limit' in generator.params
        assert 'limit' not in params
        assert ('prawtest', 'yes') in generator.params.items()
