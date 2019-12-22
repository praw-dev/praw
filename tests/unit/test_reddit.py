import configparser
import io
import types

import mock
import pytest

from praw import __version__, Reddit
from praw.config import Config
from praw.exceptions import ClientException
from prawcore import Requestor

from praw.util.validate_types import validate_types

from . import UnitTest


class CleanReddit:
    class DoesNothing:
        def __call__(self, *args, **kwargs):
            return ""

    @classmethod
    def do_nothing(cls, *a, **kw):
        return cls.DoesNothing()

    @classmethod
    def clean_new_nonrequesting_reddit(cls, *args, **params):
        reddit = Reddit(**params)
        reddit._core.request = cls.do_nothing()
        reddit._core._requestor._http = None
        return reddit


class TestReddit(CleanReddit, UnitTest):
    REQUIRED_DUMMY_SETTINGS = {
        x: "dummy" for x in ["client_id", "client_secret", "user_agent"]
    }

    @mock.patch("praw.reddit.update_check", create=True)
    @mock.patch("praw.reddit.UPDATE_CHECKER_MISSING", False)
    @mock.patch("praw.reddit.Reddit.update_checked", False)
    def test_check_for_updates(self, mock_update_check):
        Reddit(check_for_updates="1", **self.REQUIRED_DUMMY_SETTINGS)
        assert Reddit.update_checked
        mock_update_check.assert_called_with("praw", __version__)

    @mock.patch("praw.reddit.update_check", create=True)
    @mock.patch("praw.reddit.UPDATE_CHECKER_MISSING", True)
    @mock.patch("praw.reddit.Reddit.update_checked", False)
    def test_check_for_updates_update_checker_missing(self, mock_update_check):
        Reddit(check_for_updates="1", **self.REQUIRED_DUMMY_SETTINGS)
        assert not Reddit.update_checked
        assert not mock_update_check.called

    def test_comment(self):
        assert self.reddit.comment("cklfmye").id == "cklfmye"

    def test_context_manager(self):
        with Reddit(**self.REQUIRED_DUMMY_SETTINGS) as reddit:
            assert not reddit.config.check_for_updates

    def test_info__invalid_param(self):
        with pytest.raises(TypeError) as excinfo:
            self.reddit.info(None)

        err_str = "Either `fullnames` or `url` must be provided."
        assert str(excinfo.value) == err_str

        with pytest.raises(TypeError) as excinfo:
            self.reddit.info([], "")

        assert excinfo.match("(?i)mutually exclusive")

    def test_info__not_list(self):
        with pytest.raises(TypeError):
            self.reddit.info("Let's try a string")

        # assert "must be a non-str iterable" in str(excinfo.value)
        # This test has been DEPRECATED (superseded by validate_types)

    def test_live_info__valid_param(self):
        gen = self.reddit.live.info(["dummy", "dummy2"])
        assert isinstance(gen, types.GeneratorType)

    def test_live_info__invalid_param(self):
        with pytest.raises(TypeError):
            self.reddit.live.info(None)
        # assert str(excinfo.value) == "ids must be a list"
        # This test has been DEPRECATED (superseded by validate_types)

    def test_multireddit(self):
        assert self.reddit.multireddit("bboe", "aa").path == "/user/bboe/m/aa"

    def test_read_only__with_authenticated_core(self):
        with Reddit(
            password=None,
            refresh_token="refresh",
            username=None,
            **self.REQUIRED_DUMMY_SETTINGS
        ) as reddit:
            assert not reddit.read_only
            reddit.read_only = True
            assert reddit.read_only
            reddit.read_only = False
            assert not reddit.read_only

    def test_read_only__with_authenticated_core__non_confidential(self):
        with Reddit(
            client_id="dummy",
            client_secret=None,
            redirect_uri="dummy",
            user_agent="dummy",
            refresh_token="dummy",
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
        with Reddit(
            password=None, username=None, **required_settings
        ) as reddit:
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
                "Required configuration "
                "setting '{}' missing.".format(setting)
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
                "Required configuration "
                "setting '{}' missing.".format(setting)
            )

    def test_reddit__site_name_no_section(self):
        with pytest.raises(configparser.NoSectionError) as excinfo:
            Reddit("bad_site_name")
        assert "praw.readthedocs.io" in excinfo.value.message

    def test_submission(self):
        assert self.reddit.submission("2gmzqe").id == "2gmzqe"

    def test_subreddit(self):
        assert self.reddit.subreddit("redditdev").display_name == "redditdev"

    def test_valid_arg_get_path(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.get("1")
        except TypeError:
            assert False

    def test_invalid_args_get_path(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            dict(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.get(arg)

    def test_valid_arg_comment_id(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.comment(id="1")
        except TypeError:
            assert False

    def test_invalid_args_comment_id(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            dict(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.comment(id=arg)

    def test_valid_arg_info_fullnames(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.info(fullnames=["l"])
        except TypeError:
            assert False
        try:
            reddit.info(fullnames=("l",))
        except TypeError:
            assert False

    def test_invalid_args_info_fullnames(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            set(),
            dict(),
            "",
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.info(fullnames=arg)

    def test_valid_arg_info_url(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.info(url="1")
        except TypeError:
            assert False

    def test_invalid_args_info_url(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            dict(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.info(url=arg)

    def test_valid_arg_patch_path(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.patch(path="1")
        except TypeError:
            assert False

    def test_invalid_args_patch_path(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            dict(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.patch(path=arg)

    def test_valid_arg_put_path(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.put(path="1")
        except TypeError:
            assert False

    def test_invalid_args_put_path(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            dict(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.put(path=arg)

    def test_valid_arg_random_subreddit_nsfw(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )

        def just_validate(nsfw=False):
            validate_types(nsfw, (bool, int), variable_name="nsfw")

        reddit.random_subreddit = just_validate
        try:
            reddit.random_subreddit(nsfw=True)
        except TypeError:
            assert False
        try:
            reddit.random_subreddit(nsfw=False)
        except TypeError:
            assert False
        try:
            reddit.random_subreddit(nsfw=1)
        except TypeError:
            assert False
        try:
            reddit.random_subreddit(nsfw=0)
        except TypeError:
            assert False

    def test_invalid_args_random_subreddit_nsfw(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )

        def just_validate(nsfw=False):
            validate_types(nsfw, (bool, int), variable_name="nsfw")

        reddit.random_subreddit = just_validate
        invalid_args = [
            1.0,
            b"",
            complex(1),
            "",
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            dict(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.random_subreddit(nsfw=arg)

    def test_valid_arg_redditor_name(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.redditor(name="1")
        except TypeError:
            assert False

    def test_invalid_args_redditor_name(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            dict(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.redditor(name=arg)

    def test_valid_arg_redditor_fullname(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.redditor(fullname="1")
        except TypeError:
            assert False

    def test_invalid_args_redditor_fullname(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            dict(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.redditor(fullname=arg)

    def test_valid_arg_request_method(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.request("1", "")
        except TypeError:
            assert False

    def test_invalid_args_request_method(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            dict(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.request(arg, "")

    def test_valid_arg_request_path(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.request("", "1")
        except TypeError:
            assert False

    def test_invalid_args_request_path(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            dict(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.request("", arg)

    def test_valid_arg_request_params(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.request("", "", params="1")
        except TypeError:
            assert False
        try:
            reddit.request("", "", params=["1"])
        except TypeError:
            assert False
        try:
            reddit.request("", "", params=("1",))
        except TypeError:
            assert False
        try:
            reddit.request("", "", params={})
        except TypeError:
            assert False

    def test_invalid_args_request_params(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            set(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.request("", "", params=arg)

    def test_valid_arg_request_data(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.request("", "", data="{}")
        except TypeError:
            assert False
        try:
            reddit.request("", "", data={})
        except TypeError:
            assert False
        try:
            reddit.request("", "", data=b"")
        except TypeError:
            assert False
        try:
            reddit.request("", "", data=io.StringIO())
        except TypeError:
            assert False
        try:
            reddit.request("", "", data=io.BytesIO())
        except TypeError:
            assert False

    def test_invalid_args_request_data(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.request("", "", data=arg)

    def test_valid_arg_request_files(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.request("", "", files={})
        except TypeError:
            assert False

    def test_invalid_args_request_files(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            "",
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.request("", "", files=arg)

    def test_valid_arg_submission_id(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.submission(id="1")
        except TypeError:
            assert False

    def test_invalid_args_submission_id(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            dict(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.submission(id=arg)

    def test_valid_arg_submission_url(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.submission(
                url="https://www.reddit.com/r/AskReddit/comments/"
                "edwa4h/what_are_some_lesserknown_secondary_uses_for_an/"
            )
        except TypeError:
            assert False

    def test_invalid_args_submission_url(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            dict(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.submission(url=arg)

    def test_valid_arg_multireddit_redditor(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.multireddit("1", "")
        except TypeError:
            assert False

    def test_invalid_args_multireddit_redditor(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            dict(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.multireddit(arg)

    def test_valid_arg_multireddit_name(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.multireddit("test", "1")
        except TypeError:
            assert False

    def test_invalid_args_multireddit_name(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            dict(),
        ]
        for arg in invalid_args:
            print(type(arg), arg)
            with pytest.raises(TypeError):
                reddit.multireddit("test", arg)

    def test_valid_arg_subreddit_display_name(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        try:
            reddit.subreddit("1")
        except TypeError:
            assert False

    def test_invalid_args_subreddit_display_name(self):
        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy", client_secret="dummy", user_agent="dummy",
        )
        invalid_args = [
            1,
            1.0,
            b"",
            complex(1),
            True,
            False,
            object(),
            type,
            pytest,
            list(),
            tuple(),
            set(),
            dict(),
        ]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                reddit.subreddit(arg)


class TestRedditCustomRequestor(CleanReddit, UnitTest):
    def test_requestor_class(self):
        class CustomRequestor(Requestor):
            pass

        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy",
            client_secret="dummy",
            password="dummy",
            user_agent="dummy",
            username="dummy",
            requestor_class=CustomRequestor,
        )
        assert isinstance(reddit._core._requestor, CustomRequestor)
        assert not isinstance(self.reddit._core._requestor, CustomRequestor)

        reddit = self.clean_new_nonrequesting_reddit(
            client_id="dummy",
            client_secret="dummy",
            user_agent="dummy",
            requestor_class=CustomRequestor,
        )
        assert isinstance(reddit._core._requestor, CustomRequestor)
        assert not isinstance(self.reddit._core._requestor, CustomRequestor)

    def test_requestor_kwargs(self):
        session = mock.Mock(headers={})
        reddit = Reddit(
            client_id="dummy",
            client_secret="dummy",
            user_agent="dummy",
            requestor_kwargs={"session": session},
        )

        assert reddit._core._requestor._http is session
