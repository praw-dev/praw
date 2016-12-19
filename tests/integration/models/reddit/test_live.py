"""Test praw.models.LiveThread"""
from praw.models import LiveThread
import mock

from ... import IntegrationTest


class TestLiveThread(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_init(self, _):
        thread = LiveThread(self.reddit, 'ukaeu1ik4sw5')
        with self.recorder.use_cassette('TestLiveThread_test_init'):
            assert thread.title == 'reddit updates'

    @mock.patch('time.sleep', return_value=None)
    def test_updates(self, _):
        thread = LiveThread(self.reddit, 'ukaeu1ik4sw5')
        with self.recorder.use_cassette('TestLiveThread_test_updates'):
            for update in thread.updates(limit=None):
                assert update.thread == thread
        assert update.body.startswith('Small change:')
