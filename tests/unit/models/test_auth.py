"""Test praw.models.auth."""
from praw import Reddit
from praw.exceptions import ClientException
import pytest

from .. import UnitTest


def installed_app():
    return Reddit(client_id='dummy client', client_secret=None,
                  redirect_uri='https://dummy.tld/', user_agent='dummy')


def script_app():
    return Reddit(client_id='dummy client', client_secret='dummy secret',
                  password='dummy password', user_agent='dummy',
                  username='dummy username')


def web_app():
    return Reddit(client_id='dummy client', client_secret='dummy secret',
                  redirect_uri='https://dummy.tld/', user_agent='dummy')


class TestAuth(UnitTest):
    def test_authorize__from_installed_app(self):
        with pytest.raises(ClientException):
            installed_app().auth.authorize('dummy code')

    def test_authorize__from_script_app(self):
        with pytest.raises(ClientException):
            script_app().auth.authorize('dummy code')

    def test_implicit__from_script_app(self):
        with pytest.raises(ClientException):
            script_app().auth.implicit('dummy token', 10, '')

    def test_url__installed_app(self):
        url = installed_app().auth.url(['dummy scope'], 'dummy state')
        assert 'client_id=dummy+client' in url
        assert 'duration=permanent' in url
        assert 'redirect_uri=https%3A%2F%2Fdummy.tld%2F' in url
        assert 'response_type=code' in url
        assert 'scope=dummy+scope' in url
        assert 'state=dummy+state' in url

    def test_url__installed_app__implicit(self):
        url = installed_app().auth.url(['dummy scope'], 'dummy state',
                                       implicit=True)
        assert 'client_id=dummy+client' in url
        assert 'duration=temporary' in url
        assert 'redirect_uri=https%3A%2F%2Fdummy.tld%2F' in url
        assert 'response_type=token' in url
        assert 'scope=dummy+scope' in url
        assert 'state=dummy+state' in url

    def test_url__web_app(self):
        url = web_app().auth.url(['dummy scope'], 'dummy state')
        assert 'client_id=dummy+client' in url
        assert 'secret' not in url
        assert 'redirect_uri=https%3A%2F%2Fdummy.tld%2F' in url
        assert 'response_type=code' in url
        assert 'scope=dummy+scope' in url
        assert 'state=dummy+state' in url

    def test_url__web_app__implicit(self):
        with pytest.raises(ClientException):
            web_app().auth.url(['dummy scope'], 'dummy state', implicit=True)

    def test_url__web_app_without_redirect_uri(self):
        reddit = Reddit(client_id='dummy client', client_secret='dummy secret',
                        user_agent='dummy')
        with pytest.raises(ClientException):
            reddit.auth.url(['dummy scope'], 'dummy state')
