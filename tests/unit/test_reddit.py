import mock
import pytest
from praw import __version__, Reddit
from praw.errors import RequiredConfig


class TestReddit(object):
    DUMMY_SETTINGS = {x: 'dummy' for x in
                      ['client_id', 'client_secret', 'user_agent']}

    def setup(self):
        """Setup runs before all test cases."""
        self.reddit = Reddit(client_id='dummy', client_secret='dummy',
                             user_agent='dummy')
        # Unit tests should never issue requests
        self.reddit._core._requestor._http = None

    def test_reddit_missing_required_settings(self):
        for setting in self.DUMMY_SETTINGS:
            with pytest.raises(RequiredConfig) as excinfo:
                settings = self.DUMMY_SETTINGS.copy()
                settings[setting] = None
                Reddit(**settings)
            assert excinfo.value.setting == setting

    @mock.patch('praw.reddit.update_check')
    def test_check_for_updates(self, mock_update_check):
        Reddit(check_for_updates='1', **self.DUMMY_SETTINGS)
        assert Reddit.update_checked
        mock_update_check.assert_called_with('praw', __version__)

    def test_context_manager(self):
        with Reddit(**self.DUMMY_SETTINGS) as reddit:
            assert not reddit.config.check_for_updates

    def test_random_subreddit(self):
        assert self.reddit.random_subreddit().display_name == 'redditdev'

    def test_subreddit(self):
        assert self.reddit.subreddit('redditdev').display_name == 'redditdev'

    def test_subreddit_with_random(self):
        assert self.reddit.subreddit('random').display_name != 'random'
