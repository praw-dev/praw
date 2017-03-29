from praw.models import ModmailMessage
import mock

from ... import IntegrationTest


class TestModmailConversation(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_archive(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit('all').modmail('ik72')
        with self.recorder.use_cassette(
                'TestModmailConversation.test_archive'):
            conversation.archive()
            conversation = self.reddit.subreddit('all').modmail('ik72')
            assert conversation.state == 2

    def test_reply(self):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit('all').modmail('ik72')
        with self.recorder.use_cassette('TestModmailConversation.test_reply'):
            reply = conversation.reply('A message')
        assert isinstance(reply, ModmailMessage)

    @mock.patch('time.sleep', return_value=None)
    def test_unarchive(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit('all').modmail('ik72')
        with self.recorder.use_cassette(
                'TestModmailConversation.test_unarchive'):
            conversation.unarchive()
            conversation = self.reddit.subreddit('all').modmail('ik72')
            assert conversation.state == 1
