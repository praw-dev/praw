"""Test praw.models.listing.generator."""
import pytest

from praw.models.listing.generator import ListingGenerator

from ... import UnitTest


class TestListingGenerator(UnitTest):
    def test_params_are_not_modified(self):
        params = {"prawtest": "yes"}
        generator = ListingGenerator(None, None, params=params)
        assert "limit" in generator.params
        assert "limit" not in params
        assert ("prawtest", "yes") in generator.params.items()

    def test_bad_dict(self):
        generator = ListingGenerator(None, None)
        with pytest.raises(ValueError) as excinfo:
            generator._extract_sublist({"not_users": "test value"})
        assert excinfo.value.args[0] == (
            "The generator returned a dictionary PRAW didn't recognize. File a bug"
            " report at PRAW."
        )
