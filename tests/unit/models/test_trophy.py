"""Test praw.models.Trophy."""

import pytest

from praw.models.trophy import Trophy

from .. import UnitTest


class TestTrophy(UnitTest):
    def test_equality(self, reddit):
        name = "Inciteful Link"
        trophy = Trophy(reddit, {"name": name})
        assert trophy != 5

    def test_init__reject_no_name(self, reddit):
        with pytest.raises(AssertionError):
            Trophy(reddit, {})
        with pytest.raises(AssertionError):
            Trophy(reddit, {"id": "abcd"})

    def test_init__reject_non_dict(self, reddit):
        with pytest.raises(AssertionError):
            Trophy(reddit, None)
        with pytest.raises(AssertionError):
            Trophy(reddit, "")

    def test_init__str_returns_name(self, reddit):
        name = "Inciteful Link"
        trophy = Trophy(reddit, {"name": name})
        assert str(trophy) == trophy.name == name

    def test_repr(self, reddit):
        name = "Inciteful Link"
        trophy = Trophy(reddit, {"name": name})
        assert repr(trophy) == "Trophy(name='Inciteful Link')"
