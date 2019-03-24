# coding: utf-8
from praw.exceptions import APIException, ClientException, PRAWException


class TestPRAWException(object):
    def test_inheritance(self):
        assert isinstance(PRAWException(), Exception)

    def test_str(self):
        assert str(PRAWException()) == ""
        assert str(PRAWException("foo")) == "foo"


class TestAPIException(object):
    def test_inheritance(self):
        assert isinstance(APIException(None, None, None), PRAWException)

    def test_str(self):
        exception = APIException(
            "BAD_SOMETHING", "invalid something", "some_field"
        )
        assert str(exception) == (
            "BAD_SOMETHING: 'invalid something' on field 'some_field'"
        )

    def test_str_for_localized_error_string(self):
        exception = APIException("RATELIMIT", u"実行回数が多すぎます", u"フィールド")
        assert str(exception) == (
            "RATELIMIT: '\\u5b9f\\u884c\\u56de\\u6570\\u304c\\u591a"
            "\\u3059\\u304e\\u307e\\u3059' on field "
            "'\\u30d5\\u30a3\\u30fc\\u30eb\\u30c9'"
        )


class TestClientException(object):
    def test_inheritance(self):
        assert isinstance(ClientException(), PRAWException)

    def test_str(self):
        assert str(ClientException()) == ""
        assert str(ClientException("error message")) == "error message"
