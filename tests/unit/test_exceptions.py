# coding: utf-8
from praw.exceptions import (
    APIException,
    ClientException,
    DuplicateReplaceException,
    InvalidURL,
    InvalidImplicitAuth,
    MissingRequiredAttributeException,
    MultiAPIException,
    PRAWException,
    WebSocketException,
)


class TestPRAWException:
    def test_inheritance(self):
        assert isinstance(PRAWException(), Exception)

    def test_str(self):
        assert str(PRAWException()) == ""
        assert str(PRAWException("foo")) == "foo"


class TestAPIException:
    def test_inheritance(self):
        assert isinstance(APIException(None, None, None), PRAWException)

    def test_str(self):
        exception = APIException(
            "BAD_SOMETHING", "invalid something", "some_field"
        )
        assert str(exception) == (
            "BAD_SOMETHING: 'invalid something' on field 'some_field'"
        )


class TestClientException:
    def test_inheritance(self):
        assert isinstance(ClientException(), PRAWException)

    def test_str(self):
        assert str(ClientException()) == ""
        assert str(ClientException("error message")) == "error message"


class TestDuplicateReplaceException:
    def test_inheritance(self):
        assert isinstance(DuplicateReplaceException(), ClientException)

    def test_message(self):
        assert (
            str(DuplicateReplaceException())
            == "A duplicate comment has been detected. Are you attempting to "
            "call ``replace_more_comments`` more than once?"
        )


class TestInvalidImplicitAuth:
    def test_inheritance(self):
        assert isinstance(InvalidImplicitAuth(), ClientException)

    def test_message(self):
        assert (
            str(InvalidImplicitAuth())
            == "Implicit authorization can only be used with installed apps."
        )


class TestInvalidURL:
    def test_inheritance(self):
        assert isinstance(InvalidURL(None), ClientException)

    def test_message(self):
        assert (
            str(InvalidURL("https://www.google.com"))
            == "Invalid URL: https://www.google.com"
        )

    def test_custom_message(self):
        assert (
            str(InvalidURL("https://www.google.com", message="Test custom {}"))
            == "Test custom https://www.google.com"
        )


class TestMissingRequiredAttributeException:
    def test_inheritance(self):
        assert isinstance(MissingRequiredAttributeException(), ClientException)

    def test_str(self):
        assert str(MissingRequiredAttributeException()) == ""
        assert (
            str(MissingRequiredAttributeException("error message"))
            == "error message"
        )


class TestMultipleAPIException:
    def test_inheritance(self):
        assert APIException in MultiAPIException.__bases__

    def test_new(self):
        ex_list1 = [["1", "2", "3"]]
        ex_list2 = [["1", "2", "3"], ["4", "5", "6"]]
        assert MultiAPIException(ex_list1).__class__ == APIException
        assert MultiAPIException(ex_list2).__class__ == MultiAPIException

    def test_str(self):
        ex_list = [["1", "2", "3"], ["4", "5", "6"]]
        assert (
            str(MultiAPIException(ex_list))
            == "1: '2' on field '3'\n4: '5' on field '6'"
        )

    def test_api_exception_list(self):
        ex_list = [["1", "2", "3"], ["4", "5", "6"]]
        mapi = MultiAPIException(ex_list)
        assert len(mapi.api_exceptions) == 2
        assert [
            item.__class__ == APIException for item in mapi.api_exceptions
        ].count(False) == 0


class TestWebSocketException:
    def test_inheritance(self):
        assert isinstance(WebSocketException(None, None), ClientException)

    def test_str(self):
        assert str(WebSocketException("", None)) == ""
        assert (
            str(WebSocketException("error message", None)) == "error message"
        )

    def test_exception_attr(self):
        assert WebSocketException(None, None).original_exception is None
        assert isinstance(WebSocketException(None, Exception()), Exception)
        assert (
            str(WebSocketException(None, Exception("test")).original_exception)
            == "test"
        )
