"""Tests for AuthenticatedReddit class and its mixins."""

import warnings
from praw import errors
from .helper import PRAWTest, betamax


class AuthenticatedRedditTest(PRAWTest):
    """Tests authentication from a non-moderator user."""

    def betamax_init(self):
        self.r.login(self.other_non_mod_name, self.other_non_mod_pswd,
                     disable_warning=True)

    @betamax()
    def test_cache(self):
        # Other account is "too new"
        self.r.login(self.un, self.un_pswd, disable_warning=True)

        subreddit = self.r.get_subreddit(self.sr)
        original_listing = list(subreddit.get_new(limit=5))
        subreddit.submit('Test Cache: {0}'.format(self.r.modhash), 'BODY')

        # Headers are not included in the cached key so this will have no
        # affect when the request is cached
        self.r.http.headers['SKIP_BETAMAX'] = 1

        cached_listing = list(subreddit.get_new(limit=5))
        self.assertEqual(original_listing, cached_listing)

        no_cache_listing = list(subreddit.get_new(limit=5))
        self.assertNotEqual(original_listing, no_cache_listing)

    @betamax()
    def test_create_subreddit(self):
        # Other account is "too new"
        self.r.login(self.un, self.un_pswd, disable_warning=True)

        unique_name = 'PRAW_{0}'.format(self.r.modhash)[:15]
        title = 'The {0}'.format(unique_name)
        # Verify duplicate creation raises an exception
        self.assertRaises(errors.SubredditExists, self.r.create_subreddit,
                          self.sr, 'PRAW test_create_subreddit')
        # Verify the subreddit does not exist
        self.assertRaises(errors.InvalidSubreddit,
                          next, self.r.get_subreddit(unique_name).get_new())
        # Create and verify
        self.r.create_subreddit(unique_name, title,
                                'PRAW test_create_subreddit')
        self.assertEqual(title, self.r.get_subreddit(unique_name).title)

    @betamax()
    def test_login__deprecation_warning(self):
        with warnings.catch_warnings(record=True) as warning_list:
            self.r.login(self.un, self.un_pswd)
            self.assertEqual(1, len(warning_list))
            self.assertTrue(isinstance(warning_list[0].message,
                                       DeprecationWarning))

    @betamax()
    def test_moderator_or_oauth_required__logged_in_from_reddit_obj(self):
        self.assertRaises(errors.ModeratorOrScopeRequired,
                          self.r.get_settings, self.sr)

    @betamax()
    def test_moderator_or_oauth_required__logged_in_from_submission_obj(self):
        submission = self.r.get_submission(url=self.comment_url)
        self.assertRaises(errors.ModeratorOrScopeRequired, submission.remove)

    @betamax()
    def test_moderator_or_oauth_required__logged_in_from_subreddit_obj(self):
        subreddit = self.r.get_subreddit(self.sr)
        self.assertRaises(errors.ModeratorOrScopeRequired,
                          subreddit.get_settings)

    @betamax()
    def test_moderator_required__multi(self):
        sub = self.r.get_subreddit('{0}+{1}'.format(self.sr, 'test'))
        self.assertRaises(errors.ModeratorRequired, sub.get_mod_queue)

    @betamax()
    def test_submission_hide_and_unhide_batch(self):
        sub = self.r.get_subreddit(self.sr)
        new = list(sub.get_new(limit=5, params={'show': 'all', 'count': 1}))

        self.r.hide([item.fullname for item in new])
        new = list(sub.get_new(limit=5, params={'show': 'all', 'count': 2}))
        self.assertTrue(all(item.hidden for item in new))

        self.r.unhide([item.fullname for item in new])
        new = list(sub.get_new(limit=5, params={'show': 'all', 'count': 3}))
        self.assertTrue(not any(item.hidden for item in new))


class ModFlairMixinTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax()
    def test_add_user_template(self):
        self.subreddit.add_flair_template('text', 'css', True)

    @betamax()
    def test_add_link_template(self):
        self.subreddit.add_flair_template('text', 'css', True, True)
        self.subreddit.add_flair_template(text='text', is_link=True)
        self.subreddit.add_flair_template(css_class='blah', is_link=True)
        self.subreddit.add_flair_template(is_link=True)

    @betamax()
    def test_clear_user_templates(self):
        self.subreddit.clear_flair_templates()

    @betamax()
    def test_clear_link_templates(self):
        self.subreddit.clear_flair_templates(True)

    @betamax()
    def test_get_flair_list(self):
        self.assertTrue(next(self.subreddit.get_flair_list()))
