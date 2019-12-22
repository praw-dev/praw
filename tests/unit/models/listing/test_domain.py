import pytest
from praw.models.listing.domain import DomainListing

from ... import UnitTest


class DomainTesting(UnitTest):
    def test_valid_arg_domain(self):
        try:
            DomainListing(self.reddit, domain="1")
        except TypeError:
            assert False

    def test_invalid_args_domain(self):
        invalid_args = [
            1,
            1.0,
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                DomainListing(self.reddit, domain=arg)
