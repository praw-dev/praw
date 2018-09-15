"""Test praw.models.util."""
from praw.models.trophy import Trophy
import pytest

from .. import UnitTest


class TestTrophy(UnitTest):
    def test_init__reject_no_name(self):
        with pytest.raises(AssertionError):
            Trophy(self.reddit, {})
        with pytest.raises(AssertionError):
            Trophy(self.reddit, {'id': 'abcd'})

    def test_init__reject_non_dict(self):
        with pytest.raises(AssertionError):
            Trophy(self.reddit, None)
        with pytest.raises(AssertionError):
            Trophy(self.reddit, '')

    def test_init__str_returns_name(self):
        name = 'Inciteful Link'
        trophy = Trophy(self.reddit, {'name': name})
        assert str(trophy) == trophy.name == name
