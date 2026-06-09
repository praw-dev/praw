from praw.models import ModAction

from .. import UnitTest


class TestModAction(UnitTest):
    def test_mod__already_a_redditor(self, reddit):
        action = ModAction(reddit, _data={"id": "abc"})
        redditor = reddit.redditor("spez")
        action.mod = redditor
        assert action.mod is redditor
