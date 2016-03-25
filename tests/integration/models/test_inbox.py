"""Test praw.models.inbox."""
from praw.models import Comment, Message
import mock

from .. import IntegrationTest


class TestInbox(IntegrationTest):
    def test_all(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestInbox.test_all'):
            count = 0
            for item in self.reddit.inbox.all():
                assert isinstance(item, Comment) or isinstance(item, Message)
                count += 1
            assert count == 100

    @mock.patch('time.sleep', return_value=None)
    def test_all__with_limit(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestInbox.test_all__with_limit'):
            assert len(list(self.reddit.inbox.all(limit=128))) == 128

    def test_comment_replies(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestInbox.test_comment_replies'):
            count = 0
            for item in self.reddit.inbox.comment_replies(limit=64):
                assert isinstance(item, Comment)
                assert item.parent_id.startswith(
                    self.reddit.config.kinds['comment'])
                count += 1
            assert count == 64

    @mock.patch('time.sleep', return_value=None)
    def test_mark_read(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestInbox.test_mark_read',
                match_requests_on=['uri', 'method', 'body']):
            self.reddit.inbox.mark_read(list(self.reddit.inbox.unread()))

    @mock.patch('time.sleep', return_value=None)
    def test_mark_unread(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestInbox.test_mark_unread',
                match_requests_on=['uri', 'method', 'body']):
            self.reddit.inbox.mark_unread(list(self.reddit.inbox.all()))

    def test_messages(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestInbox.test_messages'):
            count = 0
            for item in self.reddit.inbox.messages(limit=64):
                assert isinstance(item, Message)
                count += 1
            assert count == 64

    def test_sent(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestInbox.test_sent'):
            count = 0
            for item in self.reddit.inbox.sent(limit=64):
                assert isinstance(item, Message)
                assert item.author == self.reddit.config.username
                count += 1
            assert count == 64

    def test_submission_replies(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestInbox.test_submission_replies'):
            count = 0
            for item in self.reddit.inbox.submission_replies(limit=64):
                assert isinstance(item, Comment)
                assert item.parent_id.startswith(
                    self.reddit.config.kinds['submission'])
                count += 1
            assert count == 64

    @mock.patch('time.sleep', return_value=None)
    def test_unread(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestInbox.test_unread'):
            count = 0
            for item in self.reddit.inbox.unread(limit=64):
                count += 1
            assert count == 64
