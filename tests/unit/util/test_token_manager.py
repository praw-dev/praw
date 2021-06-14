"""Test praw.util.refresh_token_manager."""
import sys
from tempfile import NamedTemporaryFile
from unittest import mock

import pytest

from praw.util.token_manager import (
    BaseTokenManager,
    FileTokenManager,
    SQLiteTokenManager,
)

from .. import UnitTest
from ..test_reddit import DummyTokenManager


class DummyAuthorizer:
    def __init__(self, refresh_token):
        self.refresh_token = refresh_token


class TestBaseTokenManager(UnitTest):
    def test_init_base_fail(self):
        with pytest.raises(TypeError):
            BaseTokenManager()

    def test_reddit(self):
        manager = DummyTokenManager()
        manager.reddit = "dummy"
        assert manager.reddit == "dummy"

    def test_reddit__must_only_be_set_once(self):
        manager = DummyTokenManager()
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


class TestSQLiteTokenManager(UnitTest):
    def test_is_registered(self):
        manager = SQLiteTokenManager(":memory:", "dummy_key")
        assert not manager.is_registered()

    @pytest.mark.skipif(
        sys.platform.startswith("win"), reason="this test fails on windows"
    )
    def test_multiple_instances(self):
        with NamedTemporaryFile() as fp:
            manager1 = SQLiteTokenManager(fp.name, "dummy_key1")
            manager2 = SQLiteTokenManager(fp.name, "dummy_key1")
            manager3 = SQLiteTokenManager(fp.name, "dummy_key2")

            manager1.register("dummy_value1")
            assert manager2.is_registered()
            assert not manager3.is_registered()

    def test_post_refresh_token_callback__sets_value(self):
        authorizer = DummyAuthorizer("dummy_value")
        manager = SQLiteTokenManager(":memory:", "dummy_key")

        manager.post_refresh_callback(authorizer)
        assert authorizer.refresh_token is None
        assert manager._get() == "dummy_value"

    def test_post_refresh_token_callback__updates_value(self):
        authorizer = DummyAuthorizer("dummy_value_updated")
        manager = SQLiteTokenManager(":memory:", "dummy_key")
        manager.register("dummy_value")

        manager.post_refresh_callback(authorizer)
        assert authorizer.refresh_token is None
        assert manager._get() == "dummy_value_updated"

    def test_pre_refresh_token_callback(self):
        authorizer = DummyAuthorizer(None)
        manager = SQLiteTokenManager(":memory:", "dummy_key")
        manager.register("dummy_value")

        manager.pre_refresh_callback(authorizer)
        assert authorizer.refresh_token == "dummy_value"

    def test_pre_refresh_token_callback__raises_key_error(self):
        authorizer = DummyAuthorizer(None)
        manager = SQLiteTokenManager(":memory:", "dummy_key")

        with pytest.raises(KeyError):
            manager.pre_refresh_callback(authorizer)

    def test_register(self):
        manager = SQLiteTokenManager(":memory:", "dummy_key")
        assert manager.register("dummy_value")
        assert manager.is_registered()
        assert not manager.register("dummy_value2")
        assert manager._get() == "dummy_value"
