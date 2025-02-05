"""Test praw.models.Trophy."""

import pytest

from praw.models.trophy import Trophy

from .. import UnitTest


class TestTrophy(UnitTest):
    def test_equality(self):
        trophy1 = Trophy(None, {"name": "a"})
        trophy2 = Trophy(None, {"name": "A"})
        trophy3 = Trophy(None, {"name": "a"})
        assert trophy1 == trophy1
        assert trophy1 != trophy2
        assert trophy1 == trophy3
        assert trophy1 != "a"

    def test_hash(self):
        trophy1 = Trophy(None, {"name": "a"})
        trophy2 = Trophy(None, {"name": "A"})
        trophy3 = Trophy(None, {"name": "a"})
        assert hash(trophy1) == hash(trophy1)
        assert hash(trophy1) != hash(trophy2)
        assert hash(trophy1) == hash(trophy3)

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
