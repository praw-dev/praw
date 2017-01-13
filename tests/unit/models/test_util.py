"""Test praw.models.util."""
from praw.models.util import permissions_string

from .. import UnitTest


class TestUtil(UnitTest):
    PERMISSIONS = {'a', 'b', 'c'}

    def test_permissions_string__all_explicit(self):
        assert '-all,+b,+a,+c' == permissions_string(['b', 'a', 'c'],
                                                     self.PERMISSIONS)

    def test_permissions_string__empty_list(self):
        assert '-all' == permissions_string([], set())
        assert '-all,-a,-b,-c' == permissions_string([], self.PERMISSIONS)

    def test_permissions_string__none(self):
        assert '+all' == permissions_string(None, set())
        assert '+all' == permissions_string(None, self.PERMISSIONS)

    def test_permissions_string__with_additional_permissions(self):
        assert '-all,+d' == permissions_string(['d'], set())
        assert '-all,-a,-b,-c,+d' == permissions_string(['d'],
                                                        self.PERMISSIONS)
