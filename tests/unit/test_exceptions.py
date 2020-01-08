# coding: utf-8
from praw.exceptions import APIException, ClientException, PRAWException

from . import UnitTest


class TestPRAWException(UnitTest):
    def test_inheritance(self):
        assert isinstance(PRAWException(), Exception)

    def test_str(self):
        assert str(PRAWException()) == ""
        assert str(PRAWException("foo")) == "foo"


class TestAPIException(UnitTest):
    def test_inheritance(self):
        assert isinstance(APIException(None, None, None), PRAWException)

    def test_str(self):
        exception = APIException(
            "BAD_SOMETHING", "invalid something", "some_field"
        )
        assert str(exception) == (
            "BAD_SOMETHING: 'invalid something' on field 'some_field'"
        )


class TestClientException(UnitTest):
    def test_inheritance(self):
        assert isinstance(ClientException(), PRAWException)

    def test_str(self):
        assert str(ClientException()) == ""
        assert str(ClientException("error message")) == "error message"
