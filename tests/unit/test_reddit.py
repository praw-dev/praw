import asyncio
import configparser
import types
from unittest import mock
from unittest.mock import MagicMock

import pytest
import niquests
from prawcore import Requestor
from prawcore.exceptions import BadRequest

from praw import Reddit, __version__
from praw.config import Config
from praw.exceptions import ClientException, RedditAPIException
from praw.util.token_manager import BaseTokenManager

from . import UnitTest


class DummyTokenManager(BaseTokenManager):
    def post_refresh_callback(self, authorizer):
        pass

    def pre_refresh_callback(self, authorizer):
        pass


class TestReddit(UnitTest):
    REQUIRED_DUMMY_SETTINGS = {
        x: "dummy" for x in ["client_id", "client_secret", "user_agent"]
    }

    @staticmethod
    async def check_async(reddit):
        reddit.request(method="GET", path="path")

    @staticmethod
    def patch_request(*args, **kwargs):
        """Patch requests to return mock data on specific url."""
        response = niquests.Response()
        response._content = '{"name":"username"}'.encode("utf-8")
        response.status_code = 200
        return response

    def test_check_for_async(self, caplog):
        reddit = Reddit(**self.REQUIRED_DUMMY_SETTINGS)
        reddit._core.request = self.patch_request
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.check_async(reddit))
        log_record = caplog.records[0]
        assert log_record.levelname == "WARNING"
        assert (
            log_record.message
            == "It appears that you are using PRAW in an asynchronous environment.\nIt"
            " is strongly recommended to use Async PRAW:"
            " https://asyncpraw.readthedocs.io.\nSee"
            " https://praw.readthedocs.io/en/latest/getting_started"
            "/multiple_instances.html#discord-bots-and-asynchronous-environments"
            " for more info.\n"
        )

    def test_check_for_async__disabled(self, caplog):
        reddit = Reddit(check_for_async=False, **self.REQUIRED_DUMMY_SETTINGS)
        reddit._core.request = self.patch_request
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.check_async(reddit))
        assert caplog.records == []

    @mock.patch("praw.reddit.UPDATE_CHECKER_MISSING", False)
    @mock.patch("praw.reddit.Reddit.update_checked", False)
    @mock.patch("praw.reddit.update_check", create=True)
    def test_check_for_updates(self, mock_update_check):
        Reddit(check_for_updates="1", **self.REQUIRED_DUMMY_SETTINGS)
        assert Reddit.update_checked
        mock_update_check.assert_called_with("praw", __version__)

    @mock.patch("praw.reddit.UPDATE_CHECKER_MISSING", True)
    @mock.patch("praw.reddit.Reddit.update_checked", False)
    @mock.patch("praw.reddit.update_check", create=True)
    def test_check_for_updates_update_checker_missing(self, mock_update_check):
        Reddit(check_for_updates="1", **self.REQUIRED_DUMMY_SETTINGS)
        assert not Reddit.update_checked
        assert not mock_update_check.called

    def test_comment(self, reddit):
        assert reddit.comment("cklfmye").id == "cklfmye"

    def test_conflicting_settings(self):
        with pytest.raises(TypeError) as excinfo:
            Reddit(
                token_manager="dummy",
                refresh_token="dummy",
                **self.REQUIRED_DUMMY_SETTINGS,
            )
        assert (
            str(excinfo.value)
            == "'refresh_token' setting cannot be provided when providing "
            "'token_manager'"
        )

    def test_context_manager(self):
        with Reddit(**self.REQUIRED_DUMMY_SETTINGS) as reddit:
            assert not reddit.config.check_for_updates

    def test_info__invalid_param(self, reddit):
        with pytest.raises(TypeError) as excinfo:
            reddit.info(fullnames=None)

        err_str = "Either 'fullnames', 'url', or 'subreddits' must be provided."
        assert str(excinfo.value) == err_str

        with pytest.raises(TypeError) as excinfo:
            reddit.info(fullnames=[], url="")

        assert str(excinfo.value) == err_str

    def test_info__not_list(self, reddit):
        with pytest.raises(TypeError) as excinfo:
            reddit.info(fullnames="Let's try a string")

        assert "must be a non-str iterable" in str(excinfo.value)

    def test_invalid_config(self):
        with pytest.raises(ValueError) as excinfo:
            Reddit(timeout="test", **self.REQUIRED_DUMMY_SETTINGS)
        assert (
            excinfo.value.args[0]
            == "An incorrect config type was given for option timeout. The expected "
            "type is int, but the given value is test."
        )
        with pytest.raises(ValueError) as excinfo:
            Reddit(ratelimit_seconds="test", **self.REQUIRED_DUMMY_SETTINGS)
        assert (
            excinfo.value.args[0]
            == "An incorrect config type was given for option ratelimit_seconds. The "
            "expected type is int, but the given value is test."
        )

    def test_live_info__invalid_param(self, reddit):
        with pytest.raises(TypeError) as excinfo:
            reddit.live.info(None)
        assert str(excinfo.value) == "ids must be a list"

    def test_live_info__valid_param(self, reddit):
        gen = reddit.live.info(["dummy", "dummy2"])
        assert isinstance(gen, types.GeneratorType)

    def test_multireddit(self, reddit):
        assert reddit.multireddit(redditor="bboe", name="aa").path == "/user/bboe/m/aa"

    @mock.patch(
        "praw.Reddit.request",
        new=MagicMock(
            side_effect=[
                {
                    "json": {
                        "errors": [
                            [
                                "RATELIMIT",
                                "Some unexpected error message",
                                "ratelimit",
                            ]
                        ]
                    }
                },
            ],
        ),
    )
    @mock.patch("time.sleep", return_value=None)
    def test_post_ratelimit__invalid_rate_limit_message(self, mock_sleep, reddit):
        with pytest.raises(RedditAPIException) as exception:
            reddit.post("test")
        assert exception.value.message == "Some unexpected error message"
        mock_sleep.assert_not_called()

    @mock.patch(
        "praw.Reddit.request",
        new=MagicMock(
            side_effect=[
                {
                    "json": {
                        "errors": [
                            [
                                "RATELIMIT",
                                "You are doing that too much. Try again in 1 minute.",
                                "ratelimit",
                            ]
                        ]
                    }
                },
            ],
        ),
    )
    def test_post_ratelimit__over_threshold__minutes(self, reddit):
        with pytest.raises(RedditAPIException) as exception:
            reddit.post("test")
        assert (
            exception.value.message
            == "You are doing that too much. Try again in 1 minute."
        )

    @mock.patch(
        "praw.Reddit.request",
        new=MagicMock(
            side_effect=[
                {
                    "json": {
                        "errors": [
                            [
                                "RATELIMIT",
                                "You are doing that too much. Try again in 6 seconds.",
                                "ratelimit",
                            ]
                        ]
                    }
                },
            ],
        ),
    )
    @mock.patch("time.sleep", return_value=None)
    def test_post_ratelimit__over_threshold__seconds(self, mock_sleep, reddit):
        with pytest.raises(RedditAPIException) as exception:
            reddit.post("test")
        assert (
            exception.value.message
            == "You are doing that too much. Try again in 6 seconds."
        )
        mock_sleep.assert_not_called()

    @mock.patch(
        "praw.Reddit.request",
        new=MagicMock(
            side_effect=[
                {
                    "json": {
                        "errors": [
                            [
                                "RATELIMIT",
                                "You are doing that too much. Try again in 2 "
                                "milliseconds.",
                                "ratelimit",
                            ]
                        ]
                    }
                },
                {
                    "json": {
                        "errors": [
                            [
                                "RATELIMIT",
                                "You are doing that too much. Try again in 1 "
                                "millisecond.",
                                "ratelimit",
                            ]
                        ]
                    }
                },
                {},
            ],
        ),
    )
    @mock.patch("time.sleep", return_value=None)
    def test_post_ratelimit__under_threshold__milliseconds(self, mock_sleep, reddit):
        reddit.post("test")
        mock_sleep.assert_has_calls([mock.call(1), mock.call(1)])

    @mock.patch(
        "praw.Reddit.request",
        new=MagicMock(
            side_effect=[
                {
                    "json": {
                        "errors": [
                            [
                                "RATELIMIT",
                                "You are doing that too much. Try again in 1 minute.",
                                "ratelimit",
                            ]
                        ]
                    }
                },
                {},
            ],
        ),
    )
    @mock.patch("time.sleep", return_value=None)
    def test_post_ratelimit__under_threshold__minutes(self, mock_sleep, reddit):
        reddit.config.ratelimit_seconds = 60
        reddit.post("test")
        mock_sleep.assert_has_calls([mock.call(61)])

    @mock.patch(
        "praw.Reddit.request",
        new=MagicMock(
            side_effect=[
                {
                    "json": {
                        "errors": [
                            [
                                "RATELIMIT",
                                "You are doing that too much. Try again in 5 seconds.",
                                "ratelimit",
                            ]
                        ]
                    }
                },
                {},
            ],
        ),
    )
    @mock.patch("time.sleep", return_value=None)
    def test_post_ratelimit__under_threshold__seconds(self, mock_sleep, reddit):
        reddit.post("test")
        mock_sleep.assert_has_calls([mock.call(6)])

    @mock.patch(
        "praw.Reddit.request",
        new=MagicMock(
            side_effect=[
                {
                    "json": {
                        "errors": [
                            [
                                "RATELIMIT",
                                "You are doing that too much. Try again in 5 seconds.",
                                "ratelimit",
                            ]
                        ]
                    }
                },
                {
                    "json": {
                        "errors": [
                            [
                                "RATELIMIT",
                                "You are doing that too much. Try again in 3 seconds.",
                                "ratelimit",
                            ]
                        ]
                    }
                },
                {
                    "json": {
                        "errors": [
                            [
                                "RATELIMIT",
                                "You are doing that too much. Try again in 1 second.",
                                "ratelimit",
                            ]
                        ]
                    }
                },
            ],
        ),
    )
    @mock.patch("time.sleep", return_value=None)
    def test_post_ratelimit__under_threshold__seconds_failure(self, mock_sleep, reddit):
        with pytest.raises(RedditAPIException) as exception:
            reddit.post("test")
        assert (
            exception.value.message
            == "You are doing that too much. Try again in 1 second."
        )
        mock_sleep.assert_has_calls([mock.call(6), mock.call(4), mock.call(2)])

    def test_read_only__with_authenticated_core(self):
        with Reddit(
            token_manager=DummyTokenManager(),
            password=None,
            username=None,
            **self.REQUIRED_DUMMY_SETTINGS,
        ) as reddit:
            assert not reddit.read_only
            reddit.read_only = True
            assert reddit.read_only
            reddit.read_only = False
            assert not reddit.read_only

    def test_read_only__with_authenticated_core__legacy_refresh_token(self):
        with Reddit(
            password=None,
            refresh_token="refresh",
            username=None,
            **self.REQUIRED_DUMMY_SETTINGS,
        ) as reddit:
            assert not reddit.read_only
            reddit.read_only = True
            assert reddit.read_only
            reddit.read_only = False
            assert not reddit.read_only

    def test_read_only__with_authenticated_core__non_confidential(self):
        with Reddit(
            token_manager=DummyTokenManager(),
            client_id="dummy",
            client_secret=None,
            redirect_uri="dummy",
            user_agent="dummy",
        ) as reddit:
            assert not reddit.read_only
            reddit.read_only = True
            assert reddit.read_only
            reddit.read_only = False
            assert not reddit.read_only

    def test_read_only__with_authenticated_core__non_confidential__legacy_refresh_token(
        self,
    ):
        with Reddit(
            client_id="dummy",
            client_secret=None,
            redirect_uri="dummy",
            refresh_token="dummy",
            user_agent="dummy",
        ) as reddit:
            assert not reddit.read_only
            reddit.read_only = True
            assert reddit.read_only
            reddit.read_only = False
            assert not reddit.read_only

    def test_read_only__with_script_authenticated_core(self):
        with Reddit(
            password="dummy", username="dummy", **self.REQUIRED_DUMMY_SETTINGS
        ) as reddit:
            assert not reddit.read_only
            reddit.read_only = True
            assert reddit.read_only
            reddit.read_only = False
            assert not reddit.read_only

    def test_read_only__without_trusted_authenticated_core(self):
        with Reddit(
            password=None, username=None, **self.REQUIRED_DUMMY_SETTINGS
        ) as reddit:
            assert reddit.read_only
            with pytest.raises(ClientException):
                reddit.read_only = False
            assert reddit.read_only
            reddit.read_only = True
            assert reddit.read_only

    def test_read_only__without_untrusted_authenticated_core(self):
        required_settings = self.REQUIRED_DUMMY_SETTINGS.copy()
        required_settings["client_secret"] = None
        with Reddit(password=None, username=None, **required_settings) as reddit:
            assert reddit.read_only
            with pytest.raises(ClientException):
                reddit.read_only = False
            assert reddit.read_only
            reddit.read_only = True
            assert reddit.read_only

    def test_reddit__missing_required_settings(self):
        for setting in self.REQUIRED_DUMMY_SETTINGS:
            with pytest.raises(ClientException) as excinfo:
                settings = self.REQUIRED_DUMMY_SETTINGS.copy()
                settings[setting] = Config.CONFIG_NOT_SET
                Reddit(**settings)
            assert str(excinfo.value).startswith(
                f"Required configuration setting '{setting}' missing."
            )
            if setting == "client_secret":
                assert "set to None" in str(excinfo.value)

    def test_reddit__required_settings_set_to_none(self):
        required_settings = self.REQUIRED_DUMMY_SETTINGS.copy()
        del required_settings["client_secret"]
        for setting in required_settings:
            with pytest.raises(ClientException) as excinfo:
                settings = self.REQUIRED_DUMMY_SETTINGS.copy()
                settings[setting] = None
                Reddit(**settings)
            assert str(excinfo.value).startswith(
                f"Required configuration setting '{setting}' missing."
            )

    def test_reddit__site_name_no_section(self):
        with pytest.raises(configparser.NoSectionError) as excinfo:
            Reddit("bad_site_name")
        assert "praw.readthedocs.io" in excinfo.value.message

    @mock.patch("prawcore.sessions.Session")
    def test_request__badrequest_with_no_json_body(self, mock_session):
        response = mock.Mock(status_code=400, text="")
        response.json.side_effect = ValueError
        mock_session.return_value.request = mock.Mock(
            side_effect=BadRequest(response=response)
        )

        reddit = Reddit(client_id="dummy", client_secret="dummy", user_agent="dummy")
        with pytest.raises(Exception) as excinfo:
            reddit.request(method="POST", path="/")
        assert str(excinfo.value) == "received 400 HTTP response"

    def test_request__json_and_body(self):
        reddit = Reddit(client_id="dummy", client_secret="dummy", user_agent="dummy")
        with pytest.raises(ClientException) as excinfo:
            reddit.request(
                data={"key": "value"}, json={"key": "value"}, method="POST", path="/"
            )
        assert str(excinfo.value).startswith(
            "At most one of 'data' or 'json' is supported."
        )

    def test_submission(self, reddit):
        assert reddit.submission("2gmzqe").id == "2gmzqe"

    def test_subreddit(self, reddit):
        assert reddit.subreddit("redditdev").display_name == "redditdev"


class TestRedditCustomRequestor(UnitTest):
    def test_requestor_class(self, reddit):
        class CustomRequestor(Requestor):
            pass

        _reddit = Reddit(
            requestor_class=CustomRequestor,
            client_id="dummy",
            client_secret="dummy",
            password="dummy",
            user_agent="dummy",
            username="dummy",
        )
        assert isinstance(_reddit._core._requestor, CustomRequestor)
        assert not isinstance(reddit._core._requestor, CustomRequestor)

        _reddit = Reddit(
            requestor_class=CustomRequestor,
            client_id="dummy",
            client_secret="dummy",
            user_agent="dummy",
        )
        assert isinstance(_reddit._core._requestor, CustomRequestor)
        assert not isinstance(reddit._core._requestor, CustomRequestor)

    def test_requestor_kwargs(self):
        session = mock.Mock(headers={})
        reddit = Reddit(
            requestor_kwargs={"session": session},
            client_id="dummy",
            client_secret="dummy",
            user_agent="dummy",
        )

        assert reddit._core._requestor._http is session
