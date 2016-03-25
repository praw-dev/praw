from praw.models import Message
import mock

from ... import IntegrationTest


class TestMessage(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_mark_read(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestMessage.test_mark_read'):
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
        with self.recorder.use_cassette(
                'TestMessage.test_mark_unread'):
            message = next(self.reddit.inbox.messages())
            message.mark_unread()
