"""Test praw.models.ModNote."""

from praw.models.mod_note import ModNote

from .. import UnitTest


class TestModNote(UnitTest):
    def test_equality(self):
        mod_note1 = ModNote(None, {"id": "a"})
        mod_note2 = ModNote(None, {"id": "b"})
        mod_note3 = ModNote(None, {"id": "a"})
        assert mod_note1 != mod_note2
        assert mod_note1 == mod_note3
        assert mod_note1 == "a"
        assert mod_note1 != 1
