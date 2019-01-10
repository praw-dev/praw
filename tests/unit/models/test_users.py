"""Test praw.models.users."""

from .. import UnitTest


class TestUsers(UnitTest):
    def test_search__params_not_modified(self):
        params = {'dummy': 'value'}
        generator = self.reddit.users.search(None, params=params)
        assert generator.params['dummy'] == 'value'
        assert params == {'dummy': 'value'}
