from praw.models import Message, SubredditMessage
import mock
import pytest

from ... import IntegrationTest


class TestMessage(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_block(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestMessage.test_block'):
            message = None
            for item in self.reddit.inbox.messages():
                if item.author and item.author != pytest.placeholders.username:
                    message = item
                    break
            else:
                assert False, 'no message found'
            message.block()

    @mock.patch('time.sleep', return_value=None)
    def test_mark_read(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestMessage.test_mark_read'):
            message = None
            for item in self.reddit.inbox.unread():
                if isinstance(item, Message):
                    message = item
                    break
            else:
                assert False, 'no message found in unread'
            message.mark_read()

    @mock.patch('time.sleep', return_value=None)
    def test_mark_unread(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestMessage.test_mark_unread'):
            message = next(self.reddit.inbox.messages())
            message.mark_unread()

    @mock.patch('time.sleep', return_value=None)
    def test_reply(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestMessage.test_reply'):
            message = next(self.reddit.inbox.messages())
            reply = message.reply('Message reply')
            assert reply.author == self.reddit.config.username
            assert reply.body == 'Message reply'
            assert reply.first_message_name == message.fullname


class TestSubredditMessage(IntegrationTest):
    def test_mute(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditMessage.test_mute'):
            message = SubredditMessage(self.reddit, _data={'id': '5yr8id'})
            message.mute()

    def test_unmute(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditMessage.test_unmute'):
            message = SubredditMessage(self.reddit, _data={'id': '5yr8id'})
            message.unmute()
