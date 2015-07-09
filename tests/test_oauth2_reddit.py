"""Tests for OAuth2Reddit class."""

from __future__ import print_function, unicode_literals

from praw import Reddit, errors
from praw.objects import Submission
from six import text_type
from .helper import PRAWTest, USER_AGENT, betamax


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

    @betamax()
    def test_scope_edit(self):
        self.r.refresh_access_information(self.refresh_token['edit'])
        submission = Submission.from_id(self.r, self.submission_edit_id)
        self.assertEqual(submission, submission.edit('Edited text'))

    @betamax()
    def test_scope_history(self):
        self.r.refresh_access_information(self.refresh_token['history'])
        self.assertTrue(list(self.r.get_redditor(self.un).get_upvoted()))

    @betamax()
    def test_scope_identity(self):
        self.r.refresh_access_information(self.refresh_token['identity'])
        self.assertEqual(self.un, self.r.get_me().name)

    @betamax()
    def test_scope_modconfig(self):
        self.r.refresh_access_information(self.refresh_token['modconfig'])
        self.r.get_subreddit(self.sr).set_settings('foobar')
        retval = self.r.get_subreddit(self.sr).get_stylesheet()
        self.assertTrue('images' in retval)

    @betamax()
    def test_scope_modflair(self):
        self.r.refresh_access_information(self.refresh_token['modflair'])
        self.r.get_subreddit(self.sr).set_flair(self.un, 'foobar')

    @betamax()
    def test_scope_modlog(self):
        num = 50
        self.r.refresh_access_information(self.refresh_token['modlog'])
        result = self.r.get_subreddit(self.sr).get_mod_log(limit=num)
        self.assertEqual(num, len(list(result)))

    @betamax()
    def test_scope_modothers_modself(self):
        subreddit = self.r.get_subreddit(self.sr)
        self.r.refresh_access_information(self.refresh_token['modothers'])
        subreddit.add_moderator(self.other_user_name)

        # log in as other user
        self.r.refresh_access_information(self.other_refresh_token['modself'])
        self.r.accept_moderator_invite(self.sr)

        # now return to original user.
        self.r.refresh_access_information(self.refresh_token['modothers'])
        subreddit.remove_moderator(self.other_user_name)

    @betamax()
    def test_scope_modposts(self):
        self.r.refresh_access_information(self.refresh_token['modposts'])
        Submission.from_id(self.r, self.submission_edit_id).remove()

    @betamax()
    def test_scope_mysubreddits(self):
        self.r.refresh_access_information(self.refresh_token['mysubreddits'])
        self.assertTrue(list(self.r.get_my_moderation()))

    @betamax()
    def test_scope_modwiki(self):
        self.r.refresh_access_information(self.refresh_token['wikiread'])
        subreddit = self.r.get_subreddit(self.sr)
        page = subreddit.get_wiki_page('index')
        self.r.refresh_access_information(self.refresh_token['modwiki'])
        page.add_editor(self.other_user_name)
        page.remove_editor(self.other_user_name)

    @betamax()
    def test_scope_modwiki_modcontributors(self):
        self.r.refresh_access_information(self.refresh_token['modwiki+contr'])
        subreddit = self.r.get_subreddit(self.sr)

        subreddit.add_wiki_ban(self.other_user_name)
        subreddit.remove_wiki_ban(self.other_user_name)

        subreddit.add_wiki_contributor(self.other_user_name)
        subreddit.remove_wiki_contributor(self.other_user_name)

    @betamax()
    def test_scope_creddits(self):
        # Assume there are insufficient creddits.
        self.r.refresh_access_information(
            self.refresh_token['creddits'])
        redditor = self.r.get_redditor('bboe')
        sub = self.r.get_submission(url=self.comment_url)

        # Test error conditions
        self.assertRaises(TypeError, sub.gild, months=1)
        for value in (False, 0, -1, '0', '-1'):
            self.assertRaises(TypeError, redditor.gild, value)

        # Test object gilding
        self.assertRaises(errors.InsufficientCreddits, redditor.gild)
        self.assertRaises(errors.InsufficientCreddits, sub.gild)
        self.assertRaises(errors.InsufficientCreddits, sub.comments[0].gild)

    @betamax()
    def test_scope_privatemessages(self):
        self.r.refresh_access_information(
            self.refresh_token['privatemessages'])
        self.assertTrue(list(self.r.get_inbox()))

    @betamax()
    def test_scope_read(self):
        self.r.refresh_access_information(self.refresh_token['read'])
        self.assertTrue(self.r.get_subreddit(self.priv_sr).subscribers > 0)
        fullname = '{0}_{1}'.format(self.r.config.by_object[Submission],
                                    self.priv_submission_id)
        method1 = self.r.get_info(thing_id=fullname)
        method2 = self.r.get_submission(submission_id=self.priv_submission_id)
        self.assertEqual(method1, method2)

    @betamax()
    def test_scope_read_get_front_page(self):
        self.r.refresh_access_information(self.refresh_token['mysubreddits'])
        subscribed = list(self.r.get_my_subreddits(limit=None))
        self.r.refresh_access_information(self.refresh_token['read'])
        for post in self.r.get_front_page():
            self.assertTrue(post.subreddit in subscribed)

    @betamax()
    def test_scope_read_get_sub_listingr(self):
        self.r.refresh_access_information(self.refresh_token['read'])
        subreddit = self.r.get_subreddit(self.priv_sr)
        self.assertTrue(list(subreddit.get_top()))

    @betamax()
    def test_scope_read_get_submission_by_url(self):
        url = ("https://www.reddit.com/r/reddit_api_test_priv/comments/16kbb7/"
               "google/")
        self.r.refresh_access_information(self.refresh_token['read'])
        submission = Submission.from_url(self.r, url)
        self.assertTrue(submission.num_comments != 0)

    @betamax()
    def test_scope_read_priv_sr_comments(self):
        self.r.refresh_access_information(self.refresh_token['read'])
        self.assertTrue(list(self.r.get_comments(self.priv_sr)))

    @betamax()
    def test_scope_wikiread_wiki_page(self):
        self.r.refresh_access_information(self.refresh_token['wikiread'])
        self.assertTrue(self.r.get_wiki_page(self.sr, 'index'))

    @betamax()
    def test_scope_read_priv_sub_comments(self):
        self.r.refresh_access_information(self.refresh_token['read'])
        submission = Submission.from_id(self.r, self.priv_submission_id)
        self.assertTrue(submission.comments)

    @betamax()
    def test_scope_submit(self):
        self.r.refresh_access_information(self.refresh_token['submit'])
        result = self.r.submit(self.sr, 'OAuth Submit', text='Foo')
        self.assertTrue(isinstance(result, Submission))

    @betamax()
    def test_scope_subscribe(self):
        self.r.refresh_access_information(self.refresh_token['subscribe'])
        self.r.get_subreddit(self.sr).subscribe()

    @betamax()
    def test_scope_vote(self):
        self.r.refresh_access_information(self.refresh_token['vote'])
        submission = Submission.from_id(self.r, self.submission_edit_id)
        submission.clear_vote()

    @betamax()
    def test_set_access_credentials(self):
        self.assertTrue(self.r.user is None)
        result = self.r.refresh_access_information(
            self.refresh_token['identity'], update_session=False)
        self.assertTrue(self.r.user is None)
        self.r.set_access_credentials(**result)
        self.assertFalse(self.r.user is None)

    @betamax()
    def test_oauth_without_identy_doesnt_set_user(self):
        self.assertTrue(self.r.user is None)
        self.r.refresh_access_information(self.refresh_token['edit'])
        self.assertTrue(self.r.user is None)
