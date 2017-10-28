"""Tests for OAuth2Reddit class."""

from __future__ import print_function, unicode_literals

from praw import Reddit, errors, decorators
from praw.objects import Submission
from six import text_type
from .helper import (PRAWTest, OAuthPRAWTest, USER_AGENT, betamax,
                     betamax_custom_header, mock_sys_stream)


class OAuth2RedditTest(PRAWTest):
    def setUp(self):
        self.configure()
        self.r = Reddit(USER_AGENT, site_name='reddit_oauth_test',
                        disable_update_check=True)

    def test_authorize_url(self):
        self.r.set_oauth_app_info(None, None, None)
        self.assertRaises(errors.OAuthAppRequired, self.r.get_authorize_url,
                          'dummy_state')
        self.r.set_oauth_app_info(self.r.config.client_id,
                                  self.r.config.client_secret,
                                  self.r.config.redirect_uri)
        url, params = self.r.get_authorize_url('...').split('?', 1)
        self.assertTrue('api/v1/authorize/' in url)
        params = dict(x.split('=', 1) for x in params.split('&'))
        expected = {'client_id': self.r.config.client_id,
                    'duration': 'temporary',
                    'redirect_uri': ('https%3A%2F%2F127.0.0.1%3A65010%2F'
                                     'authorize_callback'),
                    'response_type': 'code', 'scope': 'identity',
                    'state': '...'}
        self.assertEqual(expected, params)

    @betamax()
    def test_get_access_information(self):
        # If this test fails, the following URL will need to be visted in order
        # to obtain a new code to pass to `get_access_information`:
        # self.r.get_authorize_url('...')
        token = self.r.get_access_information('MQALrr1di8GzcnT8szbTWhLcBUQ')
        expected = {'access_token': self.r.access_token,
                    'refresh_token': None,
                    'scope': set(('identity',))}
        self.assertEqual(expected, token)
        self.assertEqual('PyAPITestUser2', text_type(self.r.user))

    @betamax()
    def test_get_access_information_with_invalid_code(self):
        self.assertRaises(errors.OAuthInvalidGrant,
                          self.r.get_access_information, 'invalid_code')

    def test_invalid_app_access_token(self):
        self.r.clear_authentication()
        self.r.set_oauth_app_info(None, None, None)
        self.assertRaises(errors.OAuthAppRequired,
                          self.r.get_access_information, 'dummy_code')

    def test_invalid_app_authorize_url(self):
        self.r.clear_authentication()
        self.r.set_oauth_app_info(None, None, None)
        self.assertRaises(errors.OAuthAppRequired,
                          self.r.get_authorize_url, 'dummy_state')

    @betamax()
    def test_invalid_set_access_credentials(self):
        self.assertRaises(errors.OAuthInvalidToken,
                          self.r.set_access_credentials,
                          set(('identity',)), 'dummy_access_token')

    def test_oauth_scope_required(self):
        self.r.set_oauth_app_info('dummy_client', 'dummy_secret', 'dummy_url')
        self.r.set_access_credentials(set('dummy_scope',), 'dummy_token')
        self.assertRaises(errors.OAuthScopeRequired, self.r.get_me)

    def test_raise_client_exception(self):
        def raise_client_exception(*args):
            raise errors.ClientException(*args)

        self.assertRaises(errors.ClientException, raise_client_exception)
        self.assertRaises(errors.ClientException, raise_client_exception,
                          'test')

        ce_message = errors.ClientException('Test')
        ce_no_message = errors.ClientException()
        self.assertEqual(ce_message.message, str(ce_message))
        self.assertEqual(ce_no_message.message, str(ce_no_message))

    def test_raise_http_exception(self):
        def raise_http_exception():
            raise errors.HTTPException('fakeraw')

        self.assertRaises(errors.HTTPException, raise_http_exception)
        http_exception = errors.HTTPException('fakeraw')
        self.assertEqual(http_exception.message, str(http_exception))

    def test_raise_oauth_exception(self):
        oerrormessage = "fakemessage"
        oerrorurl = "http://oauth.reddit.com/"

        def raise_oauth_exception():
            raise errors.OAuthException(oerrormessage, oerrorurl)

        self.assertRaises(errors.OAuthException, raise_oauth_exception)
        oauth_exception = errors.OAuthException(oerrormessage, oerrorurl)
        self.assertEqual(oauth_exception.message +
                         " on url {0}".format(oauth_exception.url),
                         str(oauth_exception))

    def test_raise_redirect_exception(self):
        apiurl = "http://api.reddit.com/"
        oauthurl = "http://oauth.reddit.com/"

        def raise_redirect_exception():
            raise errors.RedirectException(apiurl, oauthurl)

        self.assertRaises(errors.RedirectException, raise_redirect_exception)
        redirect_exception = errors.RedirectException(apiurl, oauthurl)
        self.assertEqual(redirect_exception.message, str(redirect_exception))


class AutoRefreshTest(OAuthPRAWTest):
    @betamax_custom_header()
    def test_auto_refresh_token(self):
        # this test wasn't cached before the new test was made
        # so the new app info needs to be set to avoid 401s
        # also, the redirect uri doesn't need to be set on refreshes,
        # but praw does this anyway. Changing this now would break
        # all prior tests. The redirect uri should be removed and
        # all tests rerecorded later.
        with self.set_custom_header_match('test_auto_refresh_token__initial'):
            self.r.refresh_access_information(
                self.refresh_token['auto_refresh'])
        old_token = self.r.access_token

        self.r.access_token += 'x'  # break the token
        with self.set_custom_header_match('test_auto_refresh_token__refresh'):
            # TODO: refreshing r.user wasn't actually updating the token
            # because of special oauth handling in _get_json_dict of
            # reddit content objects. Leaving this as a note until I
            # fix it in the future
            list(self.r.get_new(limit=5))
        current_token = self.r.access_token
        self.assertNotEqual(old_token, current_token)

        with self.set_custom_header_match('test_auto_refresh_token__after'):
            list(self.r.get_new(limit=5))
        self.assertEqual(current_token, self.r.access_token)
