from ... import UnitTest


class TestMulti(UnitTest):
    def test_repr(self):
        multi = self.reddit.multireddit("redditor", "name")
        assert repr(multi) == "<Multireddit path='/user/redditor/m/name'>"
