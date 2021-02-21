import pytest

from praw import Reddit
from praw.exceptions import ReadOnlyException
from praw.models import User

from .. import UnitTest


class TestUser(UnitTest):
    def test_me__in_read_only_mode(self):
        self.reddit = Reddit(
            client_id="dummy",
            client_secret="dummy",
            praw8_raise_exception_on_me=True,
            user_agent="dummy",
        )
        self.reddit._core._requestor._http = None

        assert self.reddit.read_only
        user = User(self.reddit)
        with pytest.raises(ReadOnlyException):
            user.me()

    def test_me__in_read_only_mode__deprecated(self):
        assert self.reddit.read_only
        assert User(self.reddit).me() is None
