# This file is part of PRAW.
#
# PRAW is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PRAW is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# PRAW.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable-msg=C0103, C0302, R0903, R0904, W0201

from __future__ import print_function

import unittest
import os

from helper import (BasicHelper, interactive_only, prompt, reddit_only,
                    USER_AGENT)
from praw import errors, Reddit
from praw.objects import Submission


class OAuth2Test(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()
        site_name = (os.getenv('REDDIT_SITE') or 'reddit') + '_oauth_test'
        self.r = Reddit(USER_AGENT, site_name=site_name,
                        disable_update_check=True)
        self.invalid = Reddit(USER_AGENT, disable_update_check=True)

    def test_authorize_url(self):
        url, params = self.r.get_authorize_url('...').split('?', 1)
        self.assertTrue('api/v1/authorize/' in url)
        params = dict(x.split('=', 1) for x in params.split('&'))
        expected = {'client_id': self.r.config.client_id,
                    'duration': 'temporary',
                    'redirect_uri': ('http%3A%2F%2F127.0.0.1%3A65010%2F'
                                     'authorize_callback'),
                    'response_type': 'code', 'scope': 'identity',
                    'state': '...'}
        self.assertEqual(expected, params)

    @interactive_only
    def test_get_access_information(self):
        print('Visit this URL: {0}'.format(self.r.get_authorize_url('...')))
        code = prompt('Code from redir URL: ')
        token = self.r.get_access_information(code)
        expected = {'access_token': self.r.access_token,
                    'refresh_token': None,
                    'scope': set(('identity',))}
        self.assertEqual(expected, token)
        self.assertNotEqual(None, self.r.user)

    def test_get_access_information_with_invalid_code(self):
        self.assertRaises(errors.OAuthInvalidGrant,
                          self.r.get_access_information, 'invalid_code')

    def test_invalid_app_access_token(self):
        self.assertRaises(errors.OAuthAppRequired,
                          self.invalid.get_access_information, 'dummy_code')

    def test_invalid_app_authorize_url(self):
        self.assertRaises(errors.OAuthAppRequired,
                          self.invalid.get_authorize_url, 'dummy_state')

    def test_invalid_set_access_credentials(self):
        self.assertRaises(errors.OAuthInvalidToken,
                          self.r.set_access_credentials,
                          set(('identity',)), 'dummy_access_token')

    @reddit_only
    def test_scope_edit(self):
        self.r.refresh_access_information(self.refresh_token['edit'])
        submission = Submission.from_id(self.r, self.submission_edit_id)
        self.assertEqual(submission, submission.edit('Edited text'))

    @reddit_only
    def test_scope_identity(self):
        self.r.refresh_access_information(self.refresh_token['identity'])
        self.assertEqual(self.un, self.r.get_me().name)

    @reddit_only
    def test_scope_modconfig(self):
        self.r.refresh_access_information(self.refresh_token['modconfig'])
        self.r.get_subreddit(self.sr).set_settings('foobar')

    @reddit_only
    def test_scope_modflair(self):
        self.r.refresh_access_information(self.refresh_token['modflair'])
        self.r.get_subreddit(self.sr).set_flair(self.un, 'foobar')

    @reddit_only
    def test_scope_modlog(self):
        self.r.refresh_access_information(self.refresh_token['modlog'])
        self.assertEqual(
            25, len(list(self.r.get_subreddit(self.sr).get_mod_log())))

    @reddit_only
    def test_scope_modposts(self):
        self.r.refresh_access_information(self.refresh_token['modposts'])
        Submission.from_id(self.r, self.submission_edit_id).remove()

    @reddit_only
    def test_scope_mysubreddits(self):
        self.r.refresh_access_information(self.refresh_token['mysubreddits'])
        self.assertTrue(list(self.r.get_my_moderation()))

    @reddit_only
    def test_scope_privatemessages(self):
        self.r.refresh_access_information(
            self.refresh_token['privatemessages'])
        self.assertTrue(list(self.r.get_inbox()))

    @reddit_only
    def test_scope_read(self):
        self.r.refresh_access_information(self.refresh_token['read'])
        self.assertTrue(self.r.get_subreddit(self.priv_sr).subscribers > 0)
        fullname = '{0}_{1}'.format(self.r.config.by_object[Submission],
                                    self.priv_submission_id)
        method1 = self.r.get_info(thing_id=fullname)
        method2 = self.r.get_submission(submission_id=self.priv_submission_id)
        self.assertEqual(method1, method2)

    @reddit_only
    def test_scope_read_get_front_page(self):
        self.r.refresh_access_information(self.refresh_token['mysubreddits'])
        subscribed = list(self.r.get_my_reddits(limit=None))
        self.r.refresh_access_information(self.refresh_token['read'])
        self.assertTrue(all(post.subreddit in subscribed
                            for post in self.r.get_front_page()))

    @reddit_only
    def test_scope_read_get_sub_listingr(self):
        self.r.refresh_access_information(self.refresh_token['read'])
        subreddit = self.r.get_subreddit(self.priv_sr)
        self.assertTrue(len(list(subreddit.get_top())))

    @reddit_only
    def test_scope_read_get_submission_by_url(self):
        url = ("http://www.reddit.com/r/reddit_api_test_priv/comments/16kbb7/"
               "google/")
        self.r.refresh_access_information(self.refresh_token['read'])
        submission = Submission.from_url(self.r, url)
        self.assertTrue(submission.num_comments != 0)

    @reddit_only
    def test_scope_read_priv_sr_comments(self):
        self.r.refresh_access_information(self.refresh_token['read'])
        self.assertTrue(len(list(self.r.get_comments(self.priv_sr))))

    @reddit_only
    def test_scope_read_priv_sub_comments(self):
        self.r.refresh_access_information(self.refresh_token['read'])
        submission = Submission.from_id(self.r, self.priv_submission_id)
        self.assertTrue(len(list(submission.comments)))

    @reddit_only
    def test_scope_submit(self):
        self.r.refresh_access_information(self.refresh_token['submit'])
        retval = self.r.submit(self.sr, 'OAuth Submit', text='Foo')
        self.assertTrue(isinstance(retval, Submission))

    @reddit_only
    def test_scope_subscribe(self):
        self.r.refresh_access_information(self.refresh_token['subscribe'])
        self.r.get_subreddit(self.sr).subscribe()

    @reddit_only
    def test_scope_vote(self):
        self.r.refresh_access_information(self.refresh_token['vote'])
        submission = Submission.from_id(self.r, self.submission_edit_id)
        submission.clear_vote()

    @reddit_only
    def test_set_access_credentials(self):
        self.assertTrue(self.r.user is None)
        retval = self.r.refresh_access_information(
            self.refresh_token['identity'], update_session=False)
        self.assertTrue(self.r.user is None)
        self.r.set_access_credentials(**retval)
        self.assertFalse(self.r.user is None)

    @reddit_only
    def test_oauth_without_identy_doesnt_set_user(self):
        self.assertTrue(self.r.user is None)
        self.r.refresh_access_information(self.refresh_token['edit'])
        self.assertTrue(self.r.user is None)

    def test_set_oauth_info(self):
        self.assertRaises(errors.OAuthAppRequired,
                          self.invalid.get_authorize_url, 'dummy_state')
        self.invalid.set_oauth_app_info(self.r.client_id, self.r.client_secret,
                                        self.r.redirect_uri)
        self.invalid.get_authorize_url('dummy_state')
