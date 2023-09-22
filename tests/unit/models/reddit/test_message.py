import pickle

import pytest

from praw.models import Message, SubredditMessage

from ... import UnitTest


class TestMessage(UnitTest):
    def test_attribute_error(self, reddit):
        with pytest.raises(AttributeError):
            Message(reddit, _data={"id": "1"}).mark_as_read()

    def test_equality(self, reddit):
        message1 = Message(reddit, _data={"id": "1"})
        message2 = Message(reddit, _data={"id": "1"})
        message3 = Message(reddit, _data={"id": "2"})
        assert message1 == message1
        assert message2 == message2
        assert message3 == message3
        assert message1 == message2
        assert message2 != message3
        assert message1 != message3
        assert "1" == message1
        assert message1 == "1"

    def test_fullname(self, reddit):
        message = Message(reddit, _data={"id": "dummy"})
        assert message.fullname == "t4_dummy"

    def test_hash(self, reddit):
        message1 = Message(reddit, _data={"id": "dummy1"})
        message2 = Message(reddit, _data={"id": "dummy1"})
        message3 = Message(reddit, _data={"id": "dummy2"})
        assert hash(message1) == hash(message1)
        assert hash(message2) == hash(message2)
        assert hash(message3) == hash(message3)
        assert hash(message1) == hash(message2)
        assert hash(message2) != hash(message3)
        assert hash(message1) != hash(message3)

    def test_pickle(self, reddit):
        message = Message(reddit, _data={"id": "dummy"})
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(message, protocol=level))
            assert message == other

    def test_repr(self, reddit):
        message = Message(reddit, _data={"id": "dummy"})
        assert repr(message) == "Message(id='dummy')"

    def test_str(self, reddit):
        message = Message(reddit, _data={"id": "dummy"})
        assert str(message) == "dummy"


class TestSubredditMessage(UnitTest):
    def test_inheritance(self, reddit):
        message = SubredditMessage(reddit, _data={"id": "dummy"})
        assert isinstance(message, Message)

    def test_repr(self, reddit):
        message = SubredditMessage(reddit, _data={"id": "dummy"})
        assert repr(message) == "SubredditMessage(id='dummy')"

    def test_str(self, reddit):
        message = SubredditMessage(reddit, _data={"id": "dummy"})
        assert str(message) == "dummy"
