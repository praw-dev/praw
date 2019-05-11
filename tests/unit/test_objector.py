from . import UnitTest


class TestObjector(UnitTest):
    def test_objectify_returns_None_for_None(self):
        assert self.reddit._objector.objectify(None) is None

    def test_register(self):
        self.reddit._objector.register("int", int)
        assert "int" in self.reddit._objector.parsers
        del self.reddit._objector.parsers["int"]
