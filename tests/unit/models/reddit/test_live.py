import pickle

import pytest

from praw.models import LiveThread, LiveUpdate, Redditor
from praw.models.reddit.live import (
    LiveContributorRelationship,
    LiveThreadContribution,
    LiveUpdateContribution,
)

from ... import UnitTest


class TestLiveThread(UnitTest):
    def test_construct_success(self):
        thread_id = "ukaeu1ik4sw5"
        data = {"id": thread_id}

        thread = LiveThread(self.reddit, thread_id)
        assert isinstance(thread, LiveThread)
        assert thread.id == thread_id

        thread = LiveThread(self.reddit, _data=data)
        assert isinstance(thread, LiveThread)
        assert thread.id == thread_id

    def test_construct_failure(self):
        message = "Either `id` or `_data` must be provided."
        with pytest.raises(TypeError) as excinfo:
            LiveThread(self.reddit)
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            LiveThread(self.reddit, id="dummy", _data={"id": "dummy"})
        assert str(excinfo.value) == message

        with pytest.raises(ValueError):
            LiveThread(self.reddit, "")

    def test_contrib(self):
        thread_id = "ukaeu1ik4sw5"
        thread = LiveThread(self.reddit, thread_id)
        assert isinstance(thread.contrib, LiveThreadContribution)

    def test_contributor(self):
        thread_id = "ukaeu1ik4sw5"
        thread = LiveThread(self.reddit, thread_id)
        assert isinstance(thread.contributor, LiveContributorRelationship)

    def test_equality(self):
        thread1 = LiveThread(self.reddit, id="dummy1")
        thread2 = LiveThread(self.reddit, id="Dummy1")
        thread3 = LiveThread(self.reddit, id="dummy3")
        assert thread1 == thread1
        assert thread2 == thread2
        assert thread3 == thread3
        assert thread1 != thread2  # live thread ID in a URL is case sensitive
        assert thread2 != thread3
        assert thread1 != thread3
        assert "dummy1" == thread1
        assert thread2 != "dummy1"
        assert thread2 == "Dummy1"

    def test_getitem(self):
        thread_id = "dummy_thread_id"
        update_id = "dummy_update_id"
        thread = LiveThread(self.reddit, id=thread_id)
        update = thread[update_id]
        assert isinstance(update, LiveUpdate)
        assert update.id == update_id

    def test_hash(self):
        thread1 = LiveThread(self.reddit, id="dummy1")
        thread2 = LiveThread(self.reddit, id="Dummy1")
        thread3 = LiveThread(self.reddit, id="dummy3")
        assert hash(thread1) == hash(thread1)
        assert hash(thread2) == hash(thread2)
        assert hash(thread3) == hash(thread3)
        assert hash(thread1) != hash(thread2)
        assert hash(thread2) != hash(thread3)
        assert hash(thread1) != hash(thread3)

    def test_pickle(self):
        thread = LiveThread(self.reddit, id="dummy")
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(thread, protocol=level))
            assert thread == other

    def test_repr(self):
        thread = LiveThread(self.reddit, id="dummy")
        assert repr(thread) == "LiveThread(id='dummy')"

    def test_str(self):
        thread = LiveThread(self.reddit, id="dummy")
        assert str(thread) == "dummy"


class TestLiveThreadContribution(UnitTest):
    def test_update__no_args(self):
        thread = LiveThread(self.reddit, "xyu8kmjvfrww")
        assert thread.contrib.update() is None


class TestLiveUpdate(UnitTest):
    def test_construct_success(self):
        thread_id = "dummy_thread_id"
        update_id = "dummy_update_id"
        data = {"id": update_id}

        update = LiveUpdate(self.reddit, thread_id=thread_id, update_id=update_id)
        assert isinstance(update, LiveUpdate)
        assert update.id == update_id
        assert isinstance(update.thread, LiveThread)
        assert update.thread.id == thread_id

        update = LiveUpdate(self.reddit, thread_id, update_id)
        assert isinstance(update, LiveUpdate)
        assert update.id == update_id
        assert isinstance(update.thread, LiveThread)
        assert update.thread.id == thread_id

        update = LiveUpdate(self.reddit, _data=data)
        assert isinstance(update, LiveUpdate)
        assert update.id == update_id
        assert update._fetched

    def test_construct_failure(self):
        message = "Either `thread_id` and `update_id`, or `_data` must be provided."
        thread_id = "dummy_thread_id"
        update_id = "dummy_update_id"

        with pytest.raises(TypeError) as excinfo:
            LiveUpdate(self.reddit)
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            LiveUpdate(self.reddit, thread_id=thread_id)
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            LiveUpdate(self.reddit, update_id=update_id)
        assert str(excinfo.value) == message

    def test_contrib(self):
        thread_id = "dummy_thread_id"
        update_id = "dummy_update_id"
        update = LiveUpdate(self.reddit, thread_id, update_id)
        assert isinstance(update.contrib, LiveUpdateContribution)

        data = {"id": "dummy_update_id", "author": "dummy_author"}
        update = LiveUpdate(self.reddit, _data=data)
        assert isinstance(update.contrib, LiveUpdateContribution)

    def test_setattr(self):
        data = {"id": "dummy_update_id", "author": "dummy_author"}
        update = LiveUpdate(self.reddit, _data=data)
        assert isinstance(update.author, Redditor)

    def test_thread(self):
        thread_id = "dummy_thread_id"
        update_id = "dummy_update_id"

        update = LiveUpdate(self.reddit, thread_id=thread_id, update_id=update_id)
        assert isinstance(update.thread, LiveThread)
        assert update.thread.id == thread_id
