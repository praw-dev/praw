"""Test praw.models.auth."""
from praw.exceptions import ClientException
import pytest

from .. import UnitTest


class TestAuth(UnitTest):
    def test_implicit(self):
        with pytest.raises(ClientException):
            self.reddit.auth.implicit('dummy token', 10, '')
