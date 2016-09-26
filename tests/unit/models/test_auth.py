"""Test praw.models.auth."""
from praw import Reddit
from praw.exceptions import ClientException
import pytest

from .. import UnitTest


class TestAuth(UnitTest):
    def test_implicit__from_script_app(self):
        with pytest.raises(ClientException):
            self.reddit.auth.implicit('dummy token', 10, '')

    def test_url__installed_app(self):
        reddit = Reddit(client_id='dummy client', client_secret=None,
                        redirect_uri='https://dummy.tld/',
                        user_agent='dummy')
        url = reddit.auth.url(['dummy scope'], 'dummy state')
        assert 'client_id=dummy+client' in url
        assert 'redirect_uri=https%3A%2F%2Fdummy.tld%2F' in url
        assert 'scope=dummy+scope' in url
        assert 'state=dummy+state' in url

    def test_url__web_app(self):
        reddit = Reddit(client_id='dummy client', client_secret='dummy secret',
                        redirect_uri='https://dummy.tld/', user_agent='dummy')
        url = reddit.auth.url(['dummy scope'], 'dummy state')
        assert 'client_id=dummy+client' in url
        assert 'secret' not in url
        assert 'redirect_uri=https%3A%2F%2Fdummy.tld%2F' in url
        assert 'scope=dummy+scope' in url
        assert 'state=dummy+state' in url

    def test_url__web_app_without_redirect_uri(self):
        reddit = Reddit(client_id='dummy client', client_secret='dummy secret',
                        user_agent='dummy')
        with pytest.raises(ClientException):
            reddit.auth.url(['dummy scope'], 'dummy state')
