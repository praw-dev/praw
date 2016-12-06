import pickle

import pytest
from praw.models import LiveThread

from ... import UnitTest


class TestLiveThread(UnitTest):

    def test_construct_success(self):
        thread_id = 'ukaeu1ik4sw5'
        data = {'id': thread_id}

        thread = LiveThread(self.reddit, thread_id)
        assert isinstance(thread, LiveThread)
        assert thread.id == thread_id

        thread = LiveThread(self.reddit, _data=data)
        assert isinstance(thread, LiveThread)
        assert thread.id == thread_id

    def test_construct_failure(self):
        message = 'Either `id` or `_data` must be provided.'
        with pytest.raises(TypeError) as excinfo:
            LiveThread(self.reddit)
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            LiveThread(self.reddit, id='dummy', _data={'id': 'dummy'})
        assert str(excinfo.value) == message

    def test_equality(self):
        thread1 = LiveThread(self.reddit, id='dummy1')
        thread2 = LiveThread(self.reddit, id='Dummy1')
        thread3 = LiveThread(self.reddit, id='dummy3')
        assert thread1 == thread1
        assert thread2 == thread2
        assert thread3 == thread3
        assert thread1 != thread2  # live thread ID in a URL is case sensitive
        assert thread2 != thread3
        assert thread1 != thread3
        assert 'dummy1' == thread1
        assert thread2 != 'dummy1'
        assert thread2 == 'Dummy1'

    def test_hash(self):
        thread1 = LiveThread(self.reddit, id='dummy1')
        thread2 = LiveThread(self.reddit, id='Dummy1')
        thread3 = LiveThread(self.reddit, id='dummy3')
        assert hash(thread1) == hash(thread1)
        assert hash(thread2) == hash(thread2)
        assert hash(thread3) == hash(thread3)
        assert hash(thread1) != hash(thread2)
        assert hash(thread2) != hash(thread3)
        assert hash(thread1) != hash(thread3)

    def test_pickle(self):
        thread = LiveThread(self.reddit, id='dummy')
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(thread, protocol=level))
            assert thread == other

    def test_repr(self):
        thread = LiveThread(self.reddit, id='dummy')
        assert repr(thread) == 'LiveThread(id=\'dummy\')'

    def test_str(self):
        thread = LiveThread(self.reddit, id='dummy')
        assert str(thread) == 'dummy'
