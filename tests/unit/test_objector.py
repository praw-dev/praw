from . import UnitTest


class TestObjector(UnitTest):
    def test_objectify_returns_None_for_None(self):
        assert self.reddit._objector.objectify(None) is None
