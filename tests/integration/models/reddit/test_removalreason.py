from praw.exceptions import ClientException
from praw.models import RemovalReason
import mock
import pytest

from ... import IntegrationTest


class TestRemovalReason(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test__fetch(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        real_id = '11qpoe6c636p5'
        fake_id = '11qaaaaaaaaaa'
        real = subreddit.removal_reasons[real_id]
        fake = subreddit.removal_reasons[fake_id]
        with self.recorder.use_cassette('TestRemovalReason.test__fetch'):
            assert real.title
            assert real.message
            assert real._fetched
            with pytest.raises(ClientException) as excinfo:
                fake.title
            assert (str(excinfo.value) ==
                    '/r/{} does not have the removal reason {}'.format(
                    subreddit, fake_id))

    @mock.patch('time.sleep', return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        reason = subreddit.removal_reasons['11qqil974lade']
        with self.recorder.use_cassette('TestRemovalReason.test_delete'):
            reason.delete()

    @mock.patch('time.sleep', return_value=None)
    def test_edit(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        reason = subreddit.removal_reasons['11qo9awftokz1']
        newmessage = "now this reason is being edited"
        with self.recorder.use_cassette('TestRemovalReason.test_edit'):
            reason.edit(reason.title, newmessage)


class TestSubredditRemovalReasons(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test__getitem(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette(
                'TestSubredditRemovalReasons.test__getitem'):
            reason1 = subreddit.removal_reasons[5]
            reason2 = subreddit.removal_reasons[reason1.id]
            assert reason1 == reason2
            assert isinstance(reason1, RemovalReason)
            assert isinstance(reason2, RemovalReason)

    @mock.patch('time.sleep', return_value=None)
    def test__iter(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette(
                'TestSubredditRemovalReasons.test__iter'):
            count = 0
            seen = set()
            for reason in subreddit.removal_reasons:
                assert isinstance(reason, RemovalReason)
                seen.add(reason)
                count += 1
            assert count > 0
            assert count == len(seen)  # No duplicates

    @mock.patch('time.sleep', return_value=None)
    def test_add(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        title = "test"
        message = "adding a test reason"
        with self.recorder.use_cassette(
                'TestSubredditRemovalReasons.test_add'):
            reason = subreddit.removal_reasons.add(title, message)
            assert isinstance(reason, RemovalReason)
            assert reason == subreddit.removal_reasons[reason.id]
            assert reason.title == title
            assert reason.message == message
