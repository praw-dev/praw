"""Test praw.util.refresh_token_manager."""
from unittest import mock

import pytest

from praw.util.token_manager import BaseTokenManager, FileTokenManager

from .. import UnitTest


class DummyAuthorizer:
    def __init__(self, refresh_token):
        self.refresh_token = refresh_token


class TestBaseTokenManager(UnitTest):
    def test_post_refresh_token_callback__raises_not_implemented(self):
        manager = BaseTokenManager()
        with pytest.raises(NotImplementedError) as excinfo:
            manager.post_refresh_callback(None)
        assert str(excinfo.value) == "``post_refresh_callback`` must be extended."

    def test_pre_refresh_token_callback__raises_not_implemented(self):
        manager = BaseTokenManager()
        with pytest.raises(NotImplementedError) as excinfo:
            manager.pre_refresh_callback(None)
        assert str(excinfo.value) == "``pre_refresh_callback`` must be extended."

    def test_reddit(self):
        manager = BaseTokenManager()
        manager.reddit = "dummy"
        assert manager.reddit == "dummy"

    def test_reddit__must_only_be_set_once(self):
        manager = BaseTokenManager()
        manager.reddit = "dummy"
        with pytest.raises(RuntimeError) as excinfo:
            manager.reddit = None
        assert (
            str(excinfo.value)
            == "``reddit`` can only be set once and is done automatically"
        )


class TestFileTokenManager(UnitTest):
    def test_post_refresh_token_callback__writes_to_file(self):
        authorizer = DummyAuthorizer("token_value")
        manager = FileTokenManager("mock/dummy_path")
        mock_open = mock.mock_open()

        with mock.patch("builtins.open", mock_open):
            manager.post_refresh_callback(authorizer)

        assert authorizer.refresh_token == "token_value"
        mock_open.assert_called_once_with("mock/dummy_path", "w")
        mock_open().write.assert_called_once_with("token_value")

    def test_pre_refresh_token_callback__reads_from_file(self):
        authorizer = DummyAuthorizer(None)
        manager = FileTokenManager("mock/dummy_path")
        mock_open = mock.mock_open(read_data="token_value")

        with mock.patch("builtins.open", mock_open):
            manager.pre_refresh_callback(authorizer)

        assert authorizer.refresh_token == "token_value"
        mock_open.assert_called_once_with("mock/dummy_path")
