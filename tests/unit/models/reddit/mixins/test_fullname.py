from praw.models.reddit.mixins.fullname import FullnameMixin

from .... import UnitTest


class TestFullnameMixin(UnitTest):
    def test_kind__defaults_to_none(self):
        class _Dummy(FullnameMixin):
            id = "abc123"

        dummy = _Dummy()
        assert dummy._kind is None
        assert dummy.fullname == "None_abc123"
