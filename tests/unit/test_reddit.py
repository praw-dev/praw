import mock
import pytest
from praw import __version__, Reddit
from praw.exceptions import ClientException

from . import UnitTest


class TestReddit(UnitTest):
    REQUIRED_DUMMY_SETTINGS = {x: 'dummy' for x in
                               ['client_id', 'client_secret', 'user_agent']}

    @mock.patch('praw.reddit.update_check', create=True)
    @mock.patch('praw.reddit.UPDATE_CHECKER_MISSING', False)
    @mock.patch('praw.reddit.Reddit.update_checked', False)
    def test_check_for_updates(self, mock_update_check):
        Reddit(check_for_updates='1', **self.REQUIRED_DUMMY_SETTINGS)
        assert Reddit.update_checked
        mock_update_check.assert_called_with('praw', __version__)

    @mock.patch('praw.reddit.update_check', create=True)
    @mock.patch('praw.reddit.UPDATE_CHECKER_MISSING', True)
    @mock.patch('praw.reddit.Reddit.update_checked', False)
    def test_check_for_updates_update_checker_missing(self, mock_update_check):
        Reddit(check_for_updates='1', **self.REQUIRED_DUMMY_SETTINGS)
        assert not Reddit.update_checked
        assert not mock_update_check.called

    def test_comment(self):
        assert self.reddit.comment('cklfmye').id == 'cklfmye'

    def test_context_manager(self):
        with Reddit(**self.REQUIRED_DUMMY_SETTINGS) as reddit:
            assert not reddit.config.check_for_updates

    def test_info__invalid_param(self):
        with pytest.raises(TypeError) as excinfo:
            print(self.reddit.info(None))

        assert str(excinfo.value) == 'fullnames must be a list'

    def test_multireddit(self):
        assert self.reddit.multireddit('bboe', 'aa').path == '/user/bboe/m/aa'

    def test_read_only__with_authenticated_core(self):
        with Reddit(password=None, refresh_token='refresh', username=None,
                    **self.REQUIRED_DUMMY_SETTINGS) as reddit:
            assert not reddit.read_only
            reddit.read_only = True
            assert reddit.read_only
            reddit.read_only = False
            assert not reddit.read_only

    def test_read_only__with_script_authenticated_core(self):
        with Reddit(password='dummy', username='dummy',
                    **self.REQUIRED_DUMMY_SETTINGS) as reddit:
            assert not reddit.read_only
            reddit.read_only = True
            assert reddit.read_only
            reddit.read_only = False
            assert not reddit.read_only

    def test_read_only__without_trusted_authenticated_core(self):
        with Reddit(password=None, username=None,
                    **self.REQUIRED_DUMMY_SETTINGS) as reddit:
            assert reddit.read_only
            with pytest.raises(ClientException):
                reddit.read_only = False
            assert reddit.read_only
            reddit.read_only = True
            assert reddit.read_only

    def test_read_only__without_untrusted_authenticated_core(self):
        required_settings = self.REQUIRED_DUMMY_SETTINGS.copy()
        required_settings['client_secret'] = None
        with Reddit(password=None, username=None,
                    **required_settings) as reddit:
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
                del settings[setting]
                Reddit(**settings)
            assert str(excinfo.value).startswith('Required configuration '
                                                 'setting \'{}\' missing.'
                                                 .format(setting))
            if setting == 'client_secret':
                assert 'set to None' in str(excinfo.value)

    def test_reddit__required_settings_set_to_none(self):
        required_settings = self.REQUIRED_DUMMY_SETTINGS.copy()
        del required_settings['client_secret']
        for setting in required_settings:
            with pytest.raises(ClientException) as excinfo:
                settings = self.REQUIRED_DUMMY_SETTINGS.copy()
                settings[setting] = None
                Reddit(**settings)
            assert str(excinfo.value).startswith('Required configuration '
                                                 'setting \'{}\' missing.'
                                                 .format(setting))

    def test_submission(self):
        assert self.reddit.submission('2gmzqe').id == '2gmzqe'

    def test_subreddit(self):
        assert self.reddit.subreddit('redditdev').display_name == 'redditdev'
