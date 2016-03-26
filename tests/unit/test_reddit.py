import mock
import pytest
from praw import __version__, Reddit
from praw.exceptions import ClientException

from . import UnitTest


class TestReddit(UnitTest):
    REQUIRED_DUMMY_SETTINGS = {x: 'dummy' for x in
                               ['client_id', 'client_secret', 'user_agent']}

    @mock.patch('praw.reddit.update_check')
    def test_check_for_updates(self, mock_update_check):
        Reddit(check_for_updates='1', **self.REQUIRED_DUMMY_SETTINGS)
        assert Reddit.update_checked
        mock_update_check.assert_called_with('praw', __version__)

    def test_comment(self):
        assert self.reddit.comment('cklfmye').id == 'cklfmye'

    def test_context_manager(self):
        with Reddit(**self.REQUIRED_DUMMY_SETTINGS) as reddit:
            assert not reddit.config.check_for_updates

    def test_read_only__with_script_authenticated_core(self):
        with Reddit(password='dummy', username='dummy',
                    **self.REQUIRED_DUMMY_SETTINGS) as reddit:
            assert not reddit.read_only
            reddit.read_only = True
            assert reddit.read_only
            reddit.read_only = False
            assert not reddit.read_only

    def test_read_only__without_authenticated_core(self):
        with Reddit(password=None, username=None,
                    **self.REQUIRED_DUMMY_SETTINGS) as reddit:
            assert reddit.read_only
            with pytest.raises(ClientException):
                reddit.read_only = False
            assert reddit.read_only
            reddit.read_only = True
            assert reddit.read_only

    def test_reddit_missing_required_settings(self):
        for setting in self.REQUIRED_DUMMY_SETTINGS:
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
