"""Test praw.util.cache."""

from .. import UnitTest

from praw.util.cache import cachedproperty


class TestCachedProperty(UnitTest):
    class Klass:
        @cachedproperty
        def nine(self):
            """Return 9."""
            return 9

        def ten(self):
            return 10

        ten = cachedproperty(ten, doc="Return 10.")

    def test_get(self):
        klass = self.Klass()
        assert "nine" not in klass.__dict__
        assert klass.nine == 9
        assert "nine" in klass.__dict__

    def test_repr(self):
        klass = self.Klass()
        assert repr(klass.nine) == "9"

        property_repr = repr(self.Klass.nine)
        assert property_repr.startswith("<cachedproperty <function")

    def test_doc(self):
        assert self.Klass.nine.__doc__ == "Return 9."
        assert self.Klass.ten.__doc__ == "Return 10."
