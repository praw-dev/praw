import pytest

from praw.models import ModmailConversation

from ... import UnitTest


class TestModmailConversation(UnitTest):
    def test_construct_failure(self):
        message = "Either `id` or `_data` must be provided."
        with pytest.raises(TypeError) as excinfo:
            ModmailConversation(self.reddit)
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            ModmailConversation(self.reddit, "dummy", _data={"id": "dummy"})
        assert str(excinfo.value) == message

    def test_str(self):
        conversation = ModmailConversation(self.reddit, _data={"id": "ik72"})

        conversation = ModmailConversation(self.reddit, "ik72")
        assert str(conversation) == "ik72"
