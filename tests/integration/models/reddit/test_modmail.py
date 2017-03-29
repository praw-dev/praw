from praw.models import ModmailMessage

from ... import IntegrationTest


class TestModmailConversation(IntegrationTest):
    def test_reply(self):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit('all').modmail('ik72')
        with self.recorder.use_cassette('TestModmailConversation.test_reply'):
            reply = conversation.reply('A message')
        assert isinstance(reply, ModmailMessage)
