"""Tests for UnauthenticatedReddit class."""

from __future__ import print_function, unicode_literals

import mock
import warnings
from six import text_type
from praw import Reddit, errors, helpers
from praw.objects import Comment, MoreComments, Submission
from .helper import PRAWTest, betamax


class UnauthenticatedRedditTest(PRAWTest):
    def test_base_36_conversion(self):
        self.assertEqual(helpers.convert_numeric_id_to_id36(295), '87')
        self.assertEqual(helpers.convert_id36_to_numeric_id('87'), 295)

        self.assertEqual(helpers.convert_numeric_id_to_id36(275492), '5wkk')
        self.assertEqual(helpers.convert_id36_to_numeric_id('5wkk'), 275492)

        self.assertRaises(TypeError, helpers.convert_numeric_id_to_id36)
        self.assertRaises(ValueError, helpers.convert_numeric_id_to_id36, '1')
        self.assertRaises(ValueError, helpers.convert_numeric_id_to_id36, -1)

        self.assertRaises(TypeError, helpers.convert_id36_to_numeric_id)
        self.assertRaises(ValueError, helpers.convert_id36_to_numeric_id,
                          't3_87')
        self.assertRaises(ValueError, helpers.convert_id36_to_numeric_id, 87)

    @betamax
    def test_comparison(self):
        self.assertEqual(self.r.get_redditor('bboe'),
                         self.r.get_redditor('BBOE'))
        self.assertEqual(self.r.get_subreddit('bboe'),
                         self.r.get_subreddit('BBOE'))

    @betamax
    def test_comments_contains_no_noncomment_objects(self):
        comments = self.r.get_submission(url=self.comment_url).comments
        self.assertFalse([item for item in comments if not
                          (isinstance(item, Comment) or
                           isinstance(item, MoreComments))])

    @betamax
    def test_create_and_delete_redditor(self):
        # This test has to be updated everytime the cassette needs to be
        # updated because we have to use consistent values for saved-runs
        # but it needs to be unique each time we actually hit reddit's
        # servers.
        key = '10'
        username = 'PyAPITestUser{0}'.format(key)
        password = 'pass{0}'.format(key)

        self.assertRaises(errors.UsernameExists, self.r.create_redditor,
                          self.other_user_name, self.other_user_pswd)

        self.r.create_redditor(username, password)
        self.r.login(username, password, disable_warning=True)
        self.assertTrue(self.r.is_logged_in())

        self.assertRaises(errors.InvalidUserPass, self.r.delete, 'bad_pswd')

        self.r.delete(password)
        self.r.clear_authentication()
        self.assertRaises(errors.InvalidUserPass, self.r.login, username,
                          password, disable_warning=True)

    @betamax
    def test_decode_entities(self):
        text = self.r.get_submission(url=self.comment_url).selftext_html
        self.assertTrue(text.startswith('<'))
        self.assertTrue(text.endswith('>'))

    @betamax
    def test_equality(self):
        subreddit = self.r.get_subreddit(self.sr)
        same_subreddit = self.r.get_subreddit(self.sr)
        submission = next(subreddit.get_hot())
        self.assertTrue(subreddit == same_subreddit)
        self.assertFalse(subreddit != same_subreddit)
        self.assertFalse(subreddit == submission)

    @betamax
    def test_get_comments(self):
        num = 50
        result = self.r.get_comments(self.sr, limit=num)
        self.assertEqual(num, len(list(result)))

    @betamax
    def test_get_comments_gilded(self):
        gilded_comments = self.r.get_comments('all', gilded_only=True)
        self.assertTrue(all(comment.gilded > 0 for comment in
                            gilded_comments))

    @betamax
    def test_get_controversial(self):
        num = 50
        result = self.r.get_controversial(limit=num, params={'t': 'all'})
        self.assertEqual(num, len(list(result)))

    @betamax
    def test_get_front_page(self):
        num = 50
        self.assertEqual(num, len(list(self.r.get_front_page(limit=num))))

    def test_login_or_oauth_required__not_logged_in(self):
        self.assertRaises(errors.LoginOrScopeRequired,
                          self.r.add_flair_template, self.sr, 'foo')

    def test_login_or_oauth_required__not_logged_in_mod_func(self):
        self.assertRaises(errors.LoginOrScopeRequired,
                          self.r.get_settings, self.sr)

    def test_login_required__not_logged_in(self):
        self.assertRaises(errors.LoginRequired, self.r.accept_moderator_invite,
                          self.sr)

    def test_login_required__not_logged_in_mod_func(self):
        self.assertRaises(errors.LoginRequired, self.r.get_banned, self.sr)

    @betamax
    def test_get_multireddit(self):
        multi_path = '/user/{0}/m/{1}'.format(self.un, self.multi_name)
        multireddit = self.r.get_multireddit(self.un, self.multi_name)
        self.assertEqual(self.multi_name.lower(),
                         text_type(multireddit).lower())
        self.assertEqual(self.un.lower(), multireddit.author.name.lower())
        self.assertEqual(multi_path.lower(), multireddit.path.lower())

    @betamax
    def test_get_new(self):
        num = 50
        result = self.r.get_new(limit=num)
        self.assertEqual(num, len(list(result)))

    @betamax
    def test_get_new_subreddits(self):
        num = 50
        self.assertEqual(num,
                         len(list(self.r.get_new_subreddits(limit=num))))

    @betamax
    def test_get_popular_subreddits(self):
        num = 50
        self.assertEqual(num,
                         len(list(self.r.get_popular_subreddits(limit=num))))

    @betamax
    def test_get_randnsfw_subreddit(self):
        subs = set()
        for _ in range(3):
            subs.add(text_type(self.r.get_subreddit('RANDNSFW')))
        self.assertTrue(len(subs) > 1)

    @betamax
    def test_get_random_subreddit(self):
        subs = set()
        for _ in range(3):
            subs.add(text_type(self.r.get_subreddit('RANDOM')))
        self.assertTrue(len(subs) > 1)

    @betamax
    def test_get_rising(self):
        num = 25
        result = self.r.get_rising(limit=num)
        self.assertEqual(num, len(list(result)))

    @betamax
    def test_get_sticky(self):
        self.assertEqual('2ujhkr', self.r.get_sticky('redditdev').id)

    @betamax
    def test_get_sticky__not_found(self):
        subreddit = self.r.get_subreddit(self.sr)
        self.assertRaises(errors.NotFound, subreddit.get_sticky)

    @betamax
    def test_get_submissions(self):
        def fullname(url):
            return self.r.get_submission(url).fullname
        fullnames = [fullname(self.comment_url), fullname(self.link_url)] * 100
        retreived = [x.fullname for x in self.r.get_submissions(fullnames)]
        self.assertEqual(fullnames, retreived)

    @mock.patch.object(Reddit, 'request_json')
    def test_get_submissions_with_params(self, mocked):
        sub = Submission(self.r, {'foo': 'meh', 'permalink': ''})
        mocked.return_value = ({'data': {'children': [sub]}},
                               {'data': {'children': []}})
        url = 'http://www.reddit.com/comments/1/_/2?context=3&foo=bar'
        self.assertEqual('meh', self.r.get_submission(url).foo)
        mocked.assert_called_with('http://www.reddit.com/comments/1/_/2',
                                  params={'context': '3', 'foo': 'bar'})

    @betamax
    def test_get_top(self):
        num = 50
        result = self.r.get_top(limit=num, params={'t': 'all'})
        self.assertEqual(num, len(list(result)))

    @betamax
    def test_info_by_id(self):
        self.assertEqual(self.link_id,
                         self.r.get_info(thing_id=self.link_id).fullname)

    @betamax
    def test_info_by_invalid_id(self):
        self.assertEqual(None, self.r.get_info(thing_id='INVALID'))

    @betamax
    def test_info_by_known_url_returns_known_id_link_post(self):
        found_links = self.r.get_info(self.link_url_link)
        tmp = self.r.get_submission(url=self.link_url)
        self.assertTrue(tmp in found_links)

    @betamax
    def test_info_by_url_also_found_by_id(self):
        found_by_url = self.r.get_info(self.link_url_link)[0]
        found_by_id = self.r.get_info(thing_id=found_by_url.fullname)
        self.assertEqual(found_by_id, found_by_url)

    @betamax
    def test_info_by_url_maximum_listing(self):
        self.assertEqual(100, len(self.r.get_info('http://www.reddit.com',
                                                  limit=101)))

    @betamax
    def test_is_username_available(self):
        self.assertFalse(self.r.is_username_available(self.un))
        self.assertTrue(self.r.is_username_available(self.invalid_user_name))
        self.assertFalse(self.r.is_username_available(''))

    def test_not_logged_in_when_initialized(self):
        self.assertEqual(self.r.user, None)

    def test_require_user_agent(self):
        self.assertRaises(TypeError, Reddit, user_agent=None)
        self.assertRaises(TypeError, Reddit, user_agent='')
        self.assertRaises(TypeError, Reddit, user_agent=1)

    @betamax
    def test_search(self):
        self.assertTrue(len(list(self.r.search('test'))) > 2)

    @betamax
    def test_search_multiply_submitted_url(self):
        self.assertTrue(
            len(list(self.r.search('http://www.livememe.com/'))) > 2)

    @betamax
    def test_search_reddit_names(self):
        self.assertTrue(self.r.search_reddit_names('reddit'))

    @betamax
    def test_search_single_submitted_url(self):
        self.assertEqual(
            1, len(list(self.r.search('http://www.livememe.com/vg972qp'))))

    @betamax
    def test_search_with_syntax(self):
        no_syntax = self.r.search('timestamp:1354348800..1354671600',
                                  subreddit=self.sr)
        self.assertFalse(list(no_syntax))
        with_syntax = self.r.search('timestamp:1354348800..1354671600',
                                    subreddit=self.sr, syntax='cloudsearch')
        self.assertTrue(list(with_syntax))

    @betamax
    def test_search_with_time_window(self):
        num = 50
        submissions = len(list(self.r.search('test', subreddit=self.sr,
                                             period='all', limit=num)))
        self.assertTrue(submissions == num)

    @betamax
    def test_store_json_result(self):
        self.r.config.store_json_result = True
        sub_url = ('http://www.reddit.com/r/reddit_api_test/comments/'
                   '1f7ojw/oauth_submit/')
        sub = self.r.get_submission(url=sub_url)
        self.assertEqual(sub.json_dict['url'], sub_url)

    @betamax
    def test_store_lazy_json_result(self):
        self.r.config.store_json_result = True
        subreddit = self.r.get_subreddit(self.sr)
        self.assertFalse(subreddit.json_dict)
        subreddit.display_name  # Force object to load
        self.assertTrue(subreddit.json_dict)

    def test_user_agent(self):
        with warnings.catch_warnings(record=True) as w:
            Reddit('robot agent')
            assert len(w) == 1
            assert isinstance(w[0].message, UserWarning)
