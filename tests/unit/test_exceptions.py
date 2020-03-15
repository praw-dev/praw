# coding: utf-8
import pytest

from praw.exceptions import (
    APIException,
    ClientException,
    DuplicateReplaceException,
    InvalidFlairTemplateID,
    InvalidImplicitAuth,
    InvalidURL,
    MissingRequiredAttributeException,
    PRAWException,
    RedditAPIException,
    RedditErrorItem,
    WebSocketException,
)


class TestPRAWException:
    def test_inheritance(self):
        assert isinstance(PRAWException(), Exception)

    def test_str(self):
        assert str(PRAWException()) == ""
        assert str(PRAWException("foo")) == "foo"


class TestRedditErrorItem:
    def test_equality(self):
        resp = ["BAD_SOMETHING", "invalid something", "some_field"]
        error = RedditErrorItem(*resp)
        error2 = RedditErrorItem(*resp)
        assert error == error2
        assert error != 0

    def test_property(self):
        error = RedditErrorItem(
            "BAD_SOMETHING", "invalid something", "some_field"
        )
        assert (
            error.error_message
            == "BAD_SOMETHING: 'invalid something' on field 'some_field'"
        )

    def test_str(self):
        error = RedditErrorItem(
            "BAD_SOMETHING", "invalid something", "some_field"
        )
        assert (
            str(error)
            == "BAD_SOMETHING: 'invalid something' on field 'some_field'"
        )

    def test_repr(self):
        error = RedditErrorItem(
            "BAD_SOMETHING", "invalid something", "some_field"
        )
        assert (
            repr(error)
            == "RedditErrorItem(error_type='BAD_SOMETHING', message="
            "'invalid something', field='some_field')"
        )


class TestAPIException:
    def test_catch(self):
        exc = RedditAPIException([["test", "testing", "test"]])
        with pytest.raises(APIException):
            raise exc


class TestRedditAPIException:
    def test_inheritance(self):
        assert issubclass(RedditAPIException, PRAWException)

    def test_items(self):
        container = RedditAPIException(
            [
                ["BAD_SOMETHING", "invalid something", "some_field"],
                RedditErrorItem(
                    "BAD_SOMETHING", "invalid something", "some_field"
                ),
            ]
        )
        for exception in container.items:
            assert isinstance(exception, RedditErrorItem)

    @pytest.mark.filterwarnings("ignore", category=DeprecationWarning)
    def test_apiexception_value(self):
        exc = RedditAPIException("test", "testing", "test")
        assert exc.error_type == "test"
        exc2 = RedditAPIException(["test", "testing", "test"])
        assert exc2.message == "testing"
        exc3 = RedditAPIException([["test", "testing", "test"]])
        assert exc3.field == "test"


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


class TestInvalidFlairTemplateID:
    def test_inheritance(self):
        assert isinstance(InvalidFlairTemplateID(None), ClientException)

    def test_str(self):
        assert (
            str(InvalidFlairTemplateID("123"))
            == "The flair template id ``123`` is invalid. If you are "
            "trying to create a flair, please use the ``add`` method."
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
