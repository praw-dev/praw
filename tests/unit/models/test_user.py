import pytest

from praw import Reddit
from praw.exceptions import ReadOnlyException
from praw.models import User

from .. import UnitTest


class TestUser(UnitTest):
    def test_me__in_read_only_mode(self, reddit):
        reddit = Reddit(
            client_id="dummy",
            client_secret="dummy",
            user_agent="dummy",
        )
        reddit._core._requestor._http = None

        assert reddit.read_only
        user = User(reddit)
        with pytest.raises(ReadOnlyException):
            user.me()
