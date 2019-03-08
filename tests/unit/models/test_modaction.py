from praw.models import ModAction, Redditor

from .. import UnitTest


class TestModAction(UnitTest):
    def test_objectify_acknowledged(self):
        data = {"mod": "dummy_author"}
        ModAction._objectify_acknowledged(self.reddit, data=data)

        redditor = data.pop("mod")
        assert type(redditor) is Redditor
        assert redditor.name == redditor.a.name == "dummy_author"
        assert data == {}

        redditor._reddit = None
        data = {"mod": redditor}
        ModAction._objectify_acknowledged(self.reddit, data=data)
        redditor = data.pop("mod")
        assert type(redditor) is Redditor
        assert redditor.name == redditor.a.name == "dummy_author"
        assert redditor._reddit is self.reddit
        assert data == {}
