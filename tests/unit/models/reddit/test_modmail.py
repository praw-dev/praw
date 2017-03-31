from praw.models import ModmailConversation

from ... import UnitTest


class TestModmailConversation(UnitTest):
    def test_parse(self):
        conversation = ModmailConversation(self.reddit,
                                           _data={'id': 'ik72'})
        assert str(conversation) == 'ik72'
