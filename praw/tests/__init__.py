#!/usr/bin/env python

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

"""Tests. Split into classes according to what they test."""

from __future__ import print_function, unicode_literals

import os
import random
import sys
import time
import unittest
import uuid
from functools import wraps
from requests.compat import urljoin
from requests.exceptions import HTTPError
from six import advance_iterator as six_next, text_type

from praw import Reddit, decorators, errors, helpers
from praw.objects import (Comment, LoggedInRedditor, Message, MoreComments,
                          Submission)

USER_AGENT = 'PRAW_test_suite'


def flair_diff(root, other):
    """Function for comparing two flairlists supporting optional arguments."""
    keys = ['user', 'flair_text', 'flair_css_class']
    root_items = set(tuple(item[key].lower() if key in item and item[key] else
                           '' for key in keys) for item in root)
    other_items = set(tuple(item[key].lower() if key in item and item[key] else
                            '' for key in keys) for item in other)
    return list(root_items - other_items)


def interactive_only(function):
    @wraps(function)
    def interactive_only_function(obj):
        if os.getenv('INTERACTIVE'):
            return function(obj)
        print('Passing interactive only test: {0}.{1}'
              .format(obj.__class__.__name__, function.__name__))
    return interactive_only_function


def local_only(function):
    @wraps(function)
    def local_only_function(obj):
        if not obj.r.config.is_reddit:
            return function(obj)
        print('Passing local only test: {0}.{1}'
              .format(obj.__class__.__name__, function.__name__))
    return local_only_function


def reddit_only(function):
    @wraps(function)
    def reddit_only_function(obj):
        if obj.r.config.is_reddit:
            return function(obj)
        print('Passing reddit only test: {0}.{1}'
              .format(obj.__class__.__name__, function.__name__))
    return reddit_only_function


def prompt(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()
    response = ''
    cur = ''
    while cur != '\n':
        cur = sys.stdin.read(1)
        response += cur
    return response.strip()


class BasicHelper(object):
    def configure(self):
        self.r = Reddit(USER_AGENT, disable_update_check=True)
        self.sr = 'reddit_api_test'
        self.priv_sr = 'reddit_api_test_priv'
        self.un = 'PyAPITestUser2'
        self.other_user_name = 'PyAPITestUser3'
        self.invalid_user_name = 'PyAPITestInvalid'

        if self.r.config.is_reddit:
            self.comment_url = self.url('/r/redditdev/comments/dtg4j/')
            self.link_url = self.url('/r/UCSantaBarbara/comments/m77nc/')
            self.link_url_link = 'http://imgur.com/Vr8ZZ'
            self.more_comments_url = self.url('/r/redditdev/comments/dqkfz/')
            self.other_user_id = '6c1xj'
            self.priv_submission_id = '16kbb7'
            self.refresh_token = {
                'edit':            'FFx_0G7Zumyh4AWzIo39bG9KdIM',
                'identity':        'E4BgmO7iho0KOB1XlT8WEtyySf8',
                'modconfig':       'bBGRgMY9Ai9_SZLZsaFvS647Mgk',
                'modflair':        'UrMbtk4bOa040XAVz0uQn2gTE3s',
                'modlog':          'ADW_EDS9-bh7Zicc7ARx7w8ZLMA',
                'modposts':        'Ffnae7s4K-uXYZB5ZaYJgh0d8DI',
                'mysubreddits':    'O7tfWhqem6fQZqxhoTiLca1s7VA',
                'privatemessages': 'kr_pHPO3sqTn_m5f_FX9TW4joEU',
                'read':            '_mmtb8YjDym0eC26G-rTxXUMea0',
                'submit':          'k69WTwa2bEQOQY9t61nItd4twhw',
                'subscribe':       'LlqwOLjyu_l6GMZIBqhcLWB0hAE',
                'vote':            '5RPnDwg56vAbf7F9yO81cXZAPSQ'}
            self.submission_edit_id = '16i92b'
        else:
            self.comment_url = self.url(
                '/r/reddit_api_test/comments/iq/_/3a7/')
            self.link_url = self.url('/r/reddit_test6/comments/y/')
            self.link_url_link = 'http://google.com/?q=29.9093488449'
            self.more_comments_url = self.url('/r/reddit_test6/comments/y/')
            self.other_user_id = 'pk'

    def delay(self, amount=None):
        if amount:
            time.sleep(amount)
        elif self.r.config.api_request_delay == 0:
            time.sleep(0.1)

    def disable_cache(self):
        self.r.config.cache_timeout = 0

    def url(self, path):
        # pylint: disable-msg=W0212
        return urljoin(self.r.config._site_url, path)


class AuthenticatedHelper(BasicHelper):
    def configure(self):
        super(AuthenticatedHelper, self).configure()
        self.r.login(self.un, '1111')


class AccessControlTests(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()

    def test_exception_get_flair_list_authenticated(self):
        self.r.login(self.un, '1111')
        self.assertTrue(self.r.get_flair_list(self.sr))

    def test_exception_get_flair_list_unauthenticated(self):
        self.assertTrue(self.r.get_flair_list(self.sr))

    def test_login_or_oauth_required_not_logged_in(self):
        self.assertRaises(errors.LoginOrScopeRequired,
                          self.r.add_flair_template, self.sr, 'foo')

    def test_login_or_oauth_required_not_logged_in_mod_func(self):
        self.assertRaises(errors.LoginOrScopeRequired,
                          self.r.get_settings, self.sr)

    def test_login_required_not_logged_in(self):
        self.assertRaises(errors.LoginRequired, self.r.accept_moderator_invite,
                          self.sr)

    def test_login_required_not_logged_in_mod_func(self):
        self.assertRaises(errors.LoginRequired, self.r.get_banned, self.sr)

    def test_oauth_scope_required(self):
        self.r.set_oauth_app_info('dummy_client', 'dummy_secret', 'dummy_url')
        self.r.set_access_credentials(set('dummy_scope',), 'dummy_token')
        self.assertRaises(errors.OAuthScopeRequired, self.r.get_me)

    def test_moderator_or_oauth_required_logged_in_from_reddit_obj(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login('PyAPITestUser4', '1111')
        self.assertRaises(errors.ModeratorOrScopeRequired,
                          oth.get_settings, self.sr)

    def test_moderator_or_oauth_required_logged_in_from_submission_obj(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login('PyAPITestUser4', '1111')
        submission = oth.get_submission(url=self.comment_url)
        self.assertRaises(errors.ModeratorOrScopeRequired, submission.remove)

    def test_moderator_or_oauth_required_logged_in_from_subreddit_obj(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login('PyAPITestUser4', '1111')
        subreddit = oth.get_subreddit(self.sr)
        self.assertRaises(errors.ModeratorOrScopeRequired,
                          subreddit.get_settings)

    def test_moderator_required_multi(self):
        self.r.login(self.un, '1111')
        sub = self.r.get_subreddit('{0}+{1}'.format(self.sr, 'test'))
        self.assertRaises(errors.ModeratorRequired, sub.get_mod_queue)

    def test_require_access_failure(self):
        self.assertRaises(TypeError, decorators.restrict_access, scope=None,
                          oauth_only=True)


class BasicTest(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()

    def test_comments_contains_no_noncomment_objects(self):
        comments = self.r.get_submission(url=self.comment_url).comments
        self.assertFalse([item for item in comments if not
                          (isinstance(item, Comment) or
                           isinstance(item, MoreComments))])

    def test_decode_entities(self):
        text = self.r.get_submission(url=self.comment_url).selftext_html
        self.assertTrue(text.startswith('&lt;'))
        self.assertTrue(text.endswith('&gt;'))
        self.r.config.decode_html_entities = True
        text = self.r.get_submission(url=self.comment_url).selftext_html
        self.assertTrue(text.startswith('<'))
        self.assertTrue(text.endswith('>'))

    def test_equality(self):
        subreddit = self.r.get_subreddit(self.sr)
        same_subreddit = self.r.get_subreddit(self.sr)
        submission = six_next(subreddit.get_hot())
        self.assertTrue(subreddit == same_subreddit)
        self.assertFalse(subreddit != same_subreddit)
        self.assertFalse(subreddit == submission)

    def test_get_comments(self):
        num = 50
        result = self.r.get_comments(self.sr, limit=num)
        self.assertEqual(num, len(list(result)))

    def test_get_comments_gilded(self):
        gilded_comments = self.r.get_comments('all', gilded_only=True)
        for comment in gilded_comments:
            self.assertTrue(comment.gilded >= 0)

    @reddit_only
    def test_get_controversial(self):
        num = 50
        result = self.r.get_controversial(limit=num, params={'t': 'all'})
        self.assertEqual(num, len(list(result)))

    def test_get_flair_list(self):
        sub = self.r.get_subreddit('python')
        self.assertTrue(six_next(sub.get_flair_list()))

    def test_get_front_page(self):
        num = 50
        self.assertEqual(num, len(list(self.r.get_front_page(limit=num))))

    def test_get_new(self):
        num = 50
        result = self.r.get_new(limit=num, params={'sort': 'new'})
        self.assertEqual(num, len(list(result)))

    @reddit_only
    def test_get_popular_subreddits(self):
        num = 50
        self.assertEqual(num,
                         len(list(self.r.get_popular_subreddits(limit=num))))

    def test_get_random_subreddit(self):
        subs = set()
        for _ in range(3):
            subs.add(self.r.get_subreddit('RANDOM').display_name)
        self.assertTrue(len(subs) > 1)

    def test_get_submissions(self):
        def fullname(url):
            return self.r.get_submission(url).fullname
        fullnames = [fullname(self.comment_url), fullname(self.link_url)] * 100
        retreived = [x.fullname for x in self.r.get_submissions(fullnames)]
        self.assertEqual(fullnames, retreived)

    @reddit_only
    def test_get_top(self):
        num = 50
        result = self.r.get_top(limit=num, params={'t': 'all'})
        self.assertEqual(num, len(list(result)))

    def test_info_by_invalid_id(self):
        self.assertEqual(None, self.r.get_info(thing_id='INVALID'))

    def test_info_by_known_url_returns_known_id_link_post(self):
        found_links = self.r.get_info(self.link_url_link)
        tmp = self.r.get_submission(url=self.link_url)
        self.assertTrue(tmp in found_links)

    def test_info_by_url_also_found_by_id(self):
        found_by_url = self.r.get_info(self.link_url_link)[0]
        found_by_id = self.r.get_info(thing_id=found_by_url.fullname)
        self.assertEqual(found_by_id, found_by_url)

    @reddit_only
    def test_info_by_url_maximum_listing(self):
        self.assertEqual(100, len(self.r.get_info('http://www.reddit.com',
                                                  limit=101)))

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

    @reddit_only
    def test_search(self):
        self.assertTrue(len(list(self.r.search('test'))) > 0)

    def test_search_reddit_names(self):
        self.assertTrue(len(self.r.search_reddit_names('reddit')) > 0)

    #def test_timeout(self):
        # pylint: disable-msg=W0212
    #    self.assertRaises(Timeout, helpers._request, self.r,
    #                      self.r.config['comments'], timeout=0.001)


class CacheTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_cache(self):
        subreddit = self.r.get_subreddit(self.sr)
        title = 'Test Cache: %s' % uuid.uuid4()
        body = "BODY"
        original_listing = list(subreddit.get_new(limit=5))
        subreddit.submit(title, body)
        new_listing = list(subreddit.get_new(limit=5))
        self.assertEqual(original_listing, new_listing)
        self.disable_cache()
        no_cache_listing = list(subreddit.get_new(limit=5))
        self.assertNotEqual(original_listing, no_cache_listing)

    def test_refresh_subreddit(self):
        self.disable_cache()
        subreddit = self.r.get_subreddit(self.sr)
        new_description = 'Description %s' % uuid.uuid4()
        subreddit.update_settings(public_description=new_description)
        self.assertNotEqual(new_description, subreddit.public_description)
        subreddit.refresh()
        self.assertEqual(new_description, subreddit.public_description)

    def test_refresh_submission(self):
        self.disable_cache()
        subreddit = self.r.get_subreddit(self.sr)
        submission = six_next(subreddit.get_top())
        same_submission = self.r.get_submission(submission_id=submission.id)
        if submission.likes:
            submission.downvote()
        else:
            submission.upvote()
        self.assertEqual(submission.likes, same_submission.likes)
        submission.refresh()
        self.assertNotEqual(submission.likes, same_submission.likes)


class EncodingTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_author_encoding(self):
        # pylint: disable-msg=E1101
        a1 = six_next(self.r.get_new()).author
        a2 = self.r.get_redditor(text_type(a1))
        self.assertEqual(a1, a2)
        s1 = six_next(a1.get_submitted())
        s2 = six_next(a2.get_submitted())
        self.assertEqual(s1, s2)

    def test_unicode_comment(self):
        sub = six_next(self.r.get_subreddit(self.sr).get_new())
        text = 'Have some unicode: (\xd0, \xdd)'
        comment = sub.add_comment(text)
        self.assertEqual(text, comment.body)

    def test_unicode_submission(self):
        unique = uuid.uuid4()
        title = 'Wiki Entry on \xC3\x9C'
        url = 'http://en.wikipedia.org/wiki/\xC3\x9C?id=%s' % unique
        submission = self.r.submit(self.sr, title, url=url)
        str(submission)
        self.assertEqual(title, submission.title)
        self.assertEqual(url, submission.url)


class MoreCommentsTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.submission = self.r.get_submission(url=self.more_comments_url,
                                                comment_limit=10)

    def test_all_comments(self):
        c_len = len(self.submission.comments)
        cf_len = len(helpers.flatten_tree(self.submission.comments))
        saved = self.submission.replace_more_comments(threshold=2)
        ac_len = len(self.submission.comments)
        acf_len = len(helpers.flatten_tree(self.submission.comments))

        # pylint: disable-msg=W0212
        self.assertEqual(len(self.submission._comments_by_id), acf_len)
        self.assertTrue(c_len < ac_len)
        self.assertTrue(c_len < cf_len)
        self.assertTrue(ac_len < acf_len)
        self.assertTrue(cf_len < acf_len)
        self.assertTrue(saved)

    def test_comments_method(self):
        for item in self.submission.comments:
            if isinstance(item, MoreComments):
                self.assertTrue(item.comments())
                break
        else:
            self.fail('Could not find MoreComment object.')


class CommentEditTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_reply(self):
        comment = six_next(self.r.user.get_comments())
        new_body = '%s\n\n+Edit Text' % comment.body
        comment = comment.edit(new_body)
        self.assertEqual(comment.body, new_body)


class CommentPermalinkTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_inbox_permalink(self):
        for item in self.r.get_inbox():
            if isinstance(item, Comment):
                self.assertTrue(item.id in item.permalink)
                break
        else:
            self.fail('Could not find comment reply in inbox')

    def test_user_comments_permalink(self):
        item = six_next(self.r.user.get_comments())
        self.assertTrue(item.id in item.permalink)

    def test_get_comments_permalink(self):
        sub = self.r.get_subreddit(self.sr)
        item = six_next(sub.get_comments())
        self.assertTrue(item.id in item.permalink)


class CommentReplyTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_add_comment_and_verify(self):
        text = 'Unique comment: %s' % uuid.uuid4()
        # pylint: disable-msg=E1101
        submission = six_next(self.subreddit.get_new())
        # pylint: enable-msg=E1101
        comment = submission.add_comment(text)
        self.assertEqual(comment.submission, submission)
        self.assertEqual(comment.body, text)

    def test_add_reply_and_verify(self):
        text = 'Unique reply: %s' % uuid.uuid4()
        found = None
        for submission in self.subreddit.get_new():
            if submission.num_comments > 0:
                found = submission
                break
        else:
            self.fail('Could not find a submission with comments.')
        comment = found.comments[0]
        reply = comment.reply(text)
        self.assertEqual(reply.parent_id, comment.fullname)
        self.assertEqual(reply.body, text)


class CommentReplyNoneTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_front_page_comment_replies_are_none(self):
        # pylint: disable-msg=E1101,W0212
        item = six_next(self.r.get_comments('all'))
        self.assertEqual(item._replies, None)

    def test_inbox_comment_replies_are_none(self):
        for item in self.r.get_inbox():
            if isinstance(item, Comment):
                # pylint: disable-msg=W0212
                self.assertEqual(item._replies, None)
                break
        else:
            self.fail('Could not find comment in inbox')

    def test_spambox_comments_replies_are_none(self):
        for item in self.r.get_subreddit(self.sr).get_spam():
            if isinstance(item, Comment):
                # pylint: disable-msg=W0212
                self.assertEqual(item._replies, None)
                break
        else:
            self.fail('Could not find comment in spambox')

    def test_user_comment_replies_are_none(self):
        for item in self.r.user.get_comments():
            if isinstance(item, Comment):
                # pylint: disable-msg=W0212
                self.assertEqual(item._replies, None)
                break
        else:
            self.fail('Could not find comment on other user\'s list')


class FlairTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_add_link_flair(self):
        flair_text = 'Flair: %s' % uuid.uuid4()
        sub = six_next(self.subreddit.get_new())
        self.subreddit.set_flair(sub, flair_text)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_text)

    def test_add_link_flair_through_submission(self):
        flair_text = 'Falir: %s' % uuid.uuid4()
        sub = six_next(self.subreddit.get_new())
        sub.set_flair(flair_text)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_text)

    def test_add_link_flair_to_invalid_subreddit(self):
        sub = six_next(self.r.get_subreddit('python').get_new())
        self.assertRaises(HTTPError, self.subreddit.set_flair, sub, 'text')

    def test_add_user_flair_by_subreddit_name(self):
        flair_text = 'Flair: %s' % uuid.uuid4()
        self.r.set_flair(self.sr, self.r.user, flair_text)
        flair = self.r.get_flair(self.sr, self.r.user)
        self.assertEqual(flair['flair_text'], flair_text)
        self.assertEqual(flair['flair_css_class'], None)

    def test_add_user_flair_to_invalid_user(self):
        self.assertRaises(errors.InvalidFlairTarget, self.subreddit.set_flair,
                          self.invalid_user_name)

    def test_add_user_flair_by_name(self):
        flair_text = 'Flair: %s' % uuid.uuid4()
        flair_css = 'a%d' % random.randint(0, 1024)
        self.subreddit.set_flair(text_type(self.r.user), flair_text, flair_css)
        flair = self.subreddit.get_flair(self.r.user)
        self.assertEqual(flair['flair_text'], flair_text)
        self.assertEqual(flair['flair_css_class'], flair_css)

    def test_clear_user_flair(self):
        self.subreddit.set_flair(self.r.user)
        flair = self.subreddit.get_flair(self.r.user)
        self.assertEqual(flair['flair_text'], None)
        self.assertEqual(flair['flair_css_class'], None)

    def test_delete_flair(self):
        flair = list(self.subreddit.get_flair_list(limit=1))[0]
        self.subreddit.delete_flair(flair['user'])
        self.assertTrue(flair not in self.subreddit.get_flair_list())

    def test_flair_csv_and_flair_list(self):
        # Clear all flair
        self.subreddit.clear_all_flair()
        self.delay(5)  # Wait for flair to clear
        self.assertEqual([], list(self.subreddit.get_flair_list()))

        # Set flair
        flair_mapping = [{'user': 'reddit', 'flair_text': 'dev'},
                         {'user': 'PyAPITestUser2', 'flair_css_class': 'xx'},
                         {'user': 'PyAPITestUser3', 'flair_text': 'AWESOME',
                          'flair_css_class': 'css'}]
        self.subreddit.set_flair_csv(flair_mapping)
        self.assertEqual([], flair_diff(flair_mapping,
                                        list(self.subreddit.get_flair_list())))

    def test_flair_csv_many(self):
        users = ('reddit', 'pyapitestuser2', 'pyapitestuser3')
        flair_text_a = 'Flair: %s' % uuid.uuid4()
        flair_text_b = 'Flair: %s' % uuid.uuid4()
        flair_mapping = [{'user': 'reddit', 'flair_text': flair_text_a}] * 99
        for user in users:
            flair_mapping.append({'user': user, 'flair_text': flair_text_b})
        self.subreddit.set_flair_csv(flair_mapping)
        for user in users:
            flair = self.subreddit.get_flair(user)
            self.assertEqual(flair['flair_text'], flair_text_b)

    def test_flair_csv_optional_args(self):
        flair_mapping = [{'user': 'reddit', 'flair_text': 'reddit'},
                         {'user': 'pyapitestuser3', 'flair_css_class': 'blah'}]
        self.subreddit.set_flair_csv(flair_mapping)

    def test_flair_csv_empty(self):
        self.assertRaises(errors.ClientException,
                          self.subreddit.set_flair_csv, [])

    def test_flair_csv_requires_user(self):
        flair_mapping = [{'flair_text': 'hsdf'}]
        self.assertRaises(errors.ClientException,
                          self.subreddit.set_flair_csv, flair_mapping)


class FlairTemplateTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_add_user_template(self):
        self.subreddit.add_flair_template('text', 'css', True)

    def test_add_link_template(self):
        self.subreddit.add_flair_template('text', 'css', True, True)
        self.subreddit.add_flair_template(text='text', is_link=True)
        self.subreddit.add_flair_template(css_class='blah', is_link=True)
        self.subreddit.add_flair_template(is_link=True)

    def test_clear_user_templates(self):
        self.subreddit.clear_flair_templates()

    def test_clear_link_templates(self):
        self.subreddit.clear_flair_templates(True)


class ImageTests(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)
        test_dir = os.path.dirname(sys.modules[__name__].__file__)
        self.image_path = os.path.join(test_dir, 'files', '{0}')

    def test_delete_header(self):
        self.subreddit.delete_image(header=True)

    def test_delete_image(self):
        images = self.subreddit.get_stylesheet()['images']
        for img_data in images[:5]:
            self.subreddit.delete_image(name=img_data['name'])
        updated_images = self.subreddit.get_stylesheet()['images']
        self.assertNotEqual(images, updated_images)

    def test_delete_invalid_image(self):
        # TODO: Patch reddit to return error when this fails
        self.subreddit.delete_image(name='invalid_image_name')

    def test_delete_invalid_params(self):
        self.assertRaises(TypeError, self.subreddit.delete_image, name='Foo',
                          header=True)

    def test_upload_invalid_file_path(self):
        self.assertRaises(IOError, self.subreddit.upload_image, 'nonexistent')

    def test_upload_uerinvalid_image(self):
        image = self.image_path.format('white-square.tiff')
        self.assertRaises(errors.ClientException, self.subreddit.upload_image,
                          image)

    def test_upload_invalid_image_too_small(self):
        image = self.image_path.format('invalid.jpg')
        self.assertRaises(errors.ClientException, self.subreddit.upload_image,
                          image)

    def test_upload_invalid_image_too_large(self):
        image = self.image_path.format('big')
        self.assertRaises(errors.ClientException, self.subreddit.upload_image,
                          image)

    def test_upload_invalid_params(self):
        image = self.image_path.format('white-square.jpg')
        self.assertRaises(TypeError, self.subreddit.upload_image, image,
                          name='Foo', header=True)

    def test_upload_invalid_image_path(self):
        self.assertRaises(IOError, self.subreddit.upload_image, 'bar.png')

    @reddit_only
    def test_upload_jpg_header(self):
        image = self.image_path.format('white-square.jpg')
        self.assertTrue(self.subreddit.upload_image(image, header=True))

    @reddit_only
    def test_upload_jpg_image(self):
        image = self.image_path.format('white-square.jpg')
        self.assertTrue(self.subreddit.upload_image(image))

    @reddit_only
    def test_upload_jpg_image_named(self):
        image = self.image_path.format('white-square.jpg')
        name = text_type(uuid.uuid4())
        self.assertTrue(self.subreddit.upload_image(image, name))
        images_json = self.subreddit.get_stylesheet()['images']
        self.assertTrue(name in text_type(x['name']) for x in images_json)

    @reddit_only
    def test_upload_jpg_image_no_extension(self):
        image = self.image_path.format('white-square')
        self.assertTrue(self.subreddit.upload_image(image))

    @reddit_only
    def test_upload_png_header(self):
        image = self.image_path.format('white-square.png')
        self.assertTrue(self.subreddit.upload_image(image, header=True))

    @reddit_only
    def test_upload_png_image(self):
        image = self.image_path.format('white-square.png')
        self.assertTrue(self.subreddit.upload_image(image))

    @reddit_only
    def test_upload_png_image_named(self):
        image = self.image_path.format('white-square.png')
        name = text_type(uuid.uuid4())
        self.assertTrue(self.subreddit.upload_image(image, name))
        images_json = self.subreddit.get_stylesheet()['images']
        self.assertTrue(name in text_type(x['name']) for x in images_json)


class LocalOnlyTest(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()

    @local_only
    def test_create_existing_redditor(self):
        self.r.login(self.un, '1111')
        self.assertRaises(errors.UsernameExists, self.r.create_redditor,
                          self.other_user_name, '1111')

    @local_only
    def test_create_existing_subreddit(self):
        self.r.login(self.un, '1111')
        self.assertRaises(errors.SubredditExists, self.r.create_subreddit,
                          self.sr, 'foo')

    @local_only
    def test_create_redditor(self):
        unique_name = 'PyAPITestUser%d' % random.randint(3, 10240)
        self.r.create_redditor(unique_name, '1111')

    @local_only
    def test_create_subreddit(self):
        unique_name = 'test%d' % random.randint(3, 10240)
        description = '#Welcome to %s\n\n0 item 1\n0 item 2\n' % unique_name
        self.r.login(self.un, '1111')
        self.r.create_subreddit(unique_name, 'The %s' % unique_name,
                                description)

    @local_only
    def test_failed_feedback(self):
        self.assertRaises(errors.InvalidEmails, self.r.send_feedback,
                          'a', 'b', 'c')

    @local_only
    def test_send_feedback(self):
        msg = 'You guys are awesome. (Sent from the PRAW python module).'
        self.r.send_feedback('Bryce Boe', 'foo@foo.com', msg)


class MessageTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_get_unread_update_has_mail(self):
        self.r.send_message(self.other_user_name, 'Update has mail', 'body')
        self.r.login(self.other_user_name, '1111')
        self.assertTrue(self.r.user.has_mail)
        self.r.get_unread(limit=1, unset_has_mail=True, update_user=True)
        self.assertFalse(self.r.user.has_mail)

    def test_mark_as_read(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login('PyAPITestUser3', '1111')
        # pylint: disable-msg=E1101
        msg = six_next(oth.get_unread(limit=1))
        msg.mark_as_read()
        self.assertTrue(msg not in oth.get_unread(limit=5))

    def test_mark_as_unread(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login('PyAPITestUser3', '1111')
        found = None
        for msg in oth.get_inbox():
            if not msg.new:
                found = msg
                msg.mark_as_unread()
                break
        else:
            self.fail('Could not find a read message.')
        self.assertTrue(found in oth.get_unread())

    def test_mark_multiple_as_read(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login('PyAPITestUser3', '1111')
        messages = []
        for msg in oth.get_unread(limit=None):
            if msg.author != oth.user.name:
                messages.append(msg)
                if len(messages) >= 2:
                    break
        self.assertEqual(2, len(messages))
        oth.user.mark_as_read(messages)
        unread = list(oth.get_unread(limit=5))
        for msg in messages:
            self.assertTrue(msg not in unread)

    def test_mod_mail_send(self):
        subject = 'Unique message: %s' % uuid.uuid4()
        self.r.get_subreddit(self.sr).send_message(subject, 'Content')
        for msg in self.r.get_mod_mail():
            if msg.subject == subject:
                break
        else:
            self.fail('Could not find the message we just sent to ourself.')

    def test_reply_to_message_and_verify(self):
        text = 'Unique message reply: %s' % uuid.uuid4()
        found = None
        for msg in self.r.get_inbox():
            if isinstance(msg, Message) and msg.author == self.r.user:
                found = msg
                break
        else:
            self.fail('Could not find a self-message in the inbox')
        reply = found.reply(text)
        self.assertEqual(reply.parent_id, found.fullname)

    def test_send(self):
        subject = 'Unique message: %s' % uuid.uuid4()
        self.r.user.send_message(subject, 'Message content')
        for msg in self.r.get_inbox():
            if msg.subject == subject:
                break
        else:
            self.fail('Could not find the message we just sent to ourself.')

    def test_send_invalid(self):
        subject = 'Unique message: %s' % uuid.uuid4()
        self.assertRaises(errors.InvalidUser, self.r.send_message,
                          self.invalid_user_name, subject, 'Message content')


class ModeratorSubmissionTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_approve(self):
        submission = six_next(self.subreddit.get_spam())
        if not submission:
            self.fail('Could not find a submission to approve.')
        submission.approve()
        for approved in self.subreddit.get_new():
            if approved.id == submission.id:
                break
        else:
            self.fail('Could not find approved submission.')

    def test_remove(self):
        submission = six_next(self.subreddit.get_new())
        if not submission:
            self.fail('Could not find a submission to remove.')
        submission.remove()
        for removed in self.subreddit.get_spam():
            if removed.id == submission.id:
                break
        else:
            self.fail('Could not find removed submission.')


class ModeratorSubredditTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_get_mod_log(self):
        self.assertTrue(list(self.subreddit.get_mod_log()))

    def test_get_mod_log_with_mod_by_name(self):
        other = self.r.get_redditor(self.other_user_name)
        actions = list(self.subreddit.get_mod_log(mod=other.name))
        self.assertTrue(actions)
        #self.assertTrue(all(x.mod_id36 == other.id for x in actions))
        self.assertTrue(all(x.mod.lower() == other.name.lower()
                            for x in actions))

    def test_get_mod_log_with_mod_by_redditor_object(self):
        other = self.r.get_redditor(self.other_user_name)
        actions = list(self.subreddit.get_mod_log(mod=other))
        self.assertTrue(actions)
        #self.assertTrue(all(x.mod_id36 == other.id for x in actions))
        self.assertTrue(all(x.mod.lower() == other.name.lower()
                            for x in actions))

    def test_get_mod_log_with_action_filter(self):
        actions = list(self.subreddit.get_mod_log(action='removelink'))
        self.assertTrue(actions)
        self.assertTrue(all(x.action == 'removelink' for x in actions))

    def test_get_mod_queue(self):
        mod_submissions = list(self.r.get_subreddit('mod').get_mod_queue())
        self.assertTrue(len(mod_submissions) > 0)

    def test_get_mod_queue_multi(self):
        multi = '{0}+{1}'.format(self.sr, 'reddit_api_test2')
        mod_submissions = list(self.r.get_subreddit(multi).get_mod_queue())
        self.assertTrue(len(mod_submissions) > 0)

    def test_get_unmoderated(self):
        submissions = list(self.subreddit.get_unmoderated())
        self.assertTrue(len(submissions) > 0)


class ModeratorUserTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)
        self.other = self.r.get_redditor('pyapitestuser3', fetch=True)

    def add_remove(self, add, remove, listing, add_callback=None):
        def test_add():
            add(self.other)
            if add_callback:
                add_callback()
            self.assertTrue(self.other in listing())

        def test_remove():
            remove(self.other)
            self.assertTrue(self.other not in listing())

        self.disable_cache()
        if self.other in listing():
            test_remove()
            test_add()
        else:
            test_add()
            test_remove()

    def test_accept_moderator_invite_fail(self):
        self.r.login('pyapitestuser3', '1111')
        self.assertRaises(errors.InvalidInvite,
                          self.subreddit.accept_moderator_invite)

    def test_ban(self):
        self.add_remove(self.subreddit.add_ban, self.subreddit.remove_ban,
                        self.subreddit.get_banned)

    def test_contributors(self):
        self.add_remove(self.subreddit.add_contributor,
                        self.subreddit.remove_contributor,
                        self.subreddit.get_contributors)

    def test_moderator(self):
        def add_callback():
            tmp = Reddit(USER_AGENT, disable_update_check=True)
            tmp.login('pyapitestuser3', '1111')
            tmp.get_subreddit(self.sr).accept_moderator_invite()

        self.add_remove(self.subreddit.add_moderator,
                        self.subreddit.remove_moderator,
                        self.subreddit.get_moderators,
                        add_callback)

    def test_make_moderator_by_name_failure(self):
        self.assertTrue(self.r.user in self.subreddit.get_moderators())
        self.assertRaises(errors.AlreadyModerator,
                          self.subreddit.add_moderator, text_type(self.r.user))

    def test_wiki_ban(self):
        self.add_remove(self.subreddit.add_wiki_ban,
                        self.subreddit.remove_wiki_ban,
                        self.subreddit.get_wiki_banned)

    def test_wiki_contributors(self):
        self.add_remove(self.subreddit.add_wiki_contributor,
                        self.subreddit.remove_wiki_contributor,
                        self.subreddit.get_wiki_contributors)


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
        subscribed = list(self.r.get_my_subreddits(limit=None))
        self.r.refresh_access_information(self.refresh_token['read'])
        for post in self.r.get_front_page():
            self.assertTrue(post.subreddit in subscribed)

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


class RedditorTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.other_user = self.r.get_redditor(self.other_user_name)

    def test_add_remove_friends(self):
        def verify_add():
            self.other_user.friend()
            self.assertTrue(self.other_user in self.r.user.get_friends())

        def verify_remove():
            self.other_user.unfriend()
            self.assertTrue(self.other_user not in self.r.user.get_friends())

        if self.other_user in self.r.user.get_friends():
            verify_remove()
            verify_add()
        else:
            verify_add()
            verify_remove()

    def test_duplicate_login(self):
        self.r.login(self.other_user_name, '1111')

    def test_get_disliked(self):
        # Pulls from get_liked. Problem here may come from get_liked
        item = six_next(self.r.user.get_liked())
        item.downvote()
        self.delay()  # The queue needs to be processed
        self.assertFalse(item in list(self.r.user.get_liked()))

    def test_get_hidden(self):
        submission = six_next(self.r.user.get_submitted())
        submission.hide()
        self.delay()  # The queue needs to be processed
        item = six_next(self.r.user.get_hidden())
        item.unhide()
        self.delay()
        self.assertFalse(item in list(self.r.user.get_hidden()))

    def test_get_liked(self):
        # Pulls from get_disliked. Problem here may come from get_disliked
        item = six_next(self.r.user.get_disliked())
        item.upvote()
        self.delay()  # The queue needs to be processed
        self.assertFalse(item in list(self.r.user.get_disliked()))

    def test_get_redditor(self):
        self.assertEqual(self.other_user_id, self.other_user.id)

    def test_user_set_on_login(self):
        self.assertTrue(isinstance(self.r.user, LoggedInRedditor))


class SettingsTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_set_settings(self):
        title = 'Reddit API Test %s' % uuid.uuid4()
        self.subreddit.set_settings(title, wikimode='anyone')
        self.assertEqual(self.subreddit.get_settings()['title'], title)

    def test_set_stylesheet(self):
        stylesheet = ('div.titlebox span.number:after {\ncontent: " %s"\n' %
                      uuid.uuid4())
        self.subreddit.set_stylesheet(stylesheet)
        self.assertEqual(stylesheet,
                         self.subreddit.get_stylesheet()['stylesheet'])

    def test_update_settings_description(self):
        self.maxDiff = None
        settings = self.subreddit.get_settings()
        settings['description'] = 'Description %s' % uuid.uuid4()
        self.subreddit.update_settings(description=settings['description'])
        new = self.subreddit.get_settings()
        # The id should change, but nothing else
        key = 'prev_description_id'
        self.assertNotEqual(settings[key], new[key])
        del settings[key]
        del new[key]
        self.assertEqual(settings, new)

    def test_update_settings_public_description(self):
        self.maxDiff = None
        settings = self.subreddit.get_settings()
        settings['public_description'] = 'Description %s' % uuid.uuid4()
        self.subreddit.update_settings(
            public_description=settings['public_description'])
        new = self.subreddit.get_settings()
        # The id should change, but nothing else
        key = 'prev_public_description_id'
        self.assertNotEqual(settings[key], new[key])
        del settings[key]
        del new[key]
        self.assertEqual(settings, new)


class SubmissionCreateTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_create_duplicate(self):
        found = None
        for item in self.r.user.get_submitted():
            if not item.is_self:
                found = item
                break
        else:
            self.fail('Could not find link post')
        self.assertRaises(errors.AlreadySubmitted, self.r.submit, self.sr,
                          found.title, url=found.url)

    def test_create_link_through_subreddit(self):
        unique = uuid.uuid4()
        title = 'Test Link: %s' % unique
        url = 'http://bryceboe.com/?bleh=%s' % unique
        subreddit = self.r.get_subreddit(self.sr)
        submission = subreddit.submit(title, url=url)
        self.assertEqual(submission.title, title)
        self.assertEqual(submission.url, url)

    def test_create_self_and_verify(self):
        title = 'Test Self: %s' % uuid.uuid4()
        content = 'BODY'
        submission = self.r.submit(self.sr, title, text=content)
        self.assertEqual(submission.title, title)
        self.assertEqual(submission.selftext, content)


class SubmissionEditTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_distinguish_and_undistinguish(self):
        def verify_distinguish(submission):
            submission.distinguish()
            submission.refresh()
            self.assertTrue(submission.distinguished)

        def verify_undistinguish(submission):
            submission.undistinguish()
            submission.refresh()
            self.assertFalse(submission.distinguished)

        self.disable_cache()
        submission = six_next(self.subreddit.get_top())
        if submission.distinguished:
            verify_undistinguish(submission)
            verify_distinguish(submission)
        else:
            verify_distinguish(submission)
            verify_undistinguish(submission)

    def test_edit_link(self):
        found = None
        for item in self.r.user.get_submitted():
            if not item.is_self:
                found = item
                break
        else:
            self.fail('Could not find link post')
        self.assertRaises(HTTPError, found.edit, 'text')

    def test_edit_self(self):
        found = None
        for item in self.r.user.get_submitted():
            if item.is_self:
                found = item
                break
        else:
            self.fail('Could not find self post')
        new_body = '%s\n\n+Edit Text' % found.selftext
        found = found.edit(new_body)
        self.assertEqual(found.selftext, new_body)

    def test_mark_as_nsfw(self):
        self.disable_cache()
        found = None
        for item in self.subreddit.get_top():
            if not item.over_18:
                found = item
                break
        else:
            self.fail("Couldn't find a SFW submission")
        found.mark_as_nsfw()
        found.refresh()
        self.assertTrue(found.over_18)

    def test_unmark_as_nsfw(self):
        self.disable_cache()
        found = None
        for item in self.subreddit.get_top():
            if item.over_18:
                found = item
                break
        else:
            self.fail("Couldn't find a NSFW submission")
        found.unmark_as_nsfw()
        found.refresh()
        self.assertFalse(found.over_18)


class SubmissionTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_clear_vote(self):
        submission = None
        for submission in self.r.user.get_submitted():
            if submission.likes is False:
                break
        else:
            self.fail('Could not find a down-voted submission.')
        submission.clear_vote()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertEqual(submission.likes, None)

    def test_delete(self):
        submission = list(self.r.user.get_submitted())[-1]
        submission.delete()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertEqual(None, submission.author)

    def test_downvote(self):
        submission = None
        for submission in self.r.user.get_submitted():
            if submission.likes is True:
                break
        else:
            self.fail('Could not find an up-voted submission.')
        submission.downvote()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertEqual(submission.likes, False)

    def test_hide(self):
        self.disable_cache()
        found = None
        for item in self.r.user.get_submitted():
            if not item.hidden:
                found = item
                break
        else:
            self.fail("Couldn't find an unhidden submission")
        found.hide()
        found.refresh()
        self.assertTrue(found.hidden)

    def test_report(self):
        # login as new user to report submission
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login('PyAPITestUser3', '1111')
        subreddit = oth.get_subreddit(self.sr)
        submission = None
        for submission in subreddit.get_new():
            if not submission.hidden:
                break
        else:
            self.fail('Could not find a non-reported submission.')
        submission.report()
        # check if submission was reported
        for report in self.r.get_subreddit(self.sr).get_reports():
            if report.id == submission.id:
                break
        else:
            self.fail('Could not find reported submission.')

    def test_save(self):
        submission = None
        for submission in self.r.user.get_submitted():
            if not submission.saved:
                break
        else:
            self.fail('Could not find unsaved submission.')
        submission.save()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertTrue(submission.saved)
        # verify in saved_links
        for item in self.r.user.get_saved():
            if item == submission:
                break
        else:
            self.fail('Could not find submission in saved links.')

    def test_short_link(self):
        submission = six_next(self.r.get_new())
        if self.r.config.is_reddit:
            self.assertTrue(submission.id in submission.short_link)
        else:
            self.assertRaises(errors.ClientException, getattr, submission,
                              'short_link')

    def test_unhide(self):
        self.disable_cache()
        found = None
        for item in self.r.user.get_submitted():
            if item.hidden:
                found = item
                break
        else:
            self.fail("Couldn't find a hidden submission")
        found.unhide()
        found.refresh()
        self.assertFalse(found.hidden)

    def test_unsave(self):
        submission = None
        for submission in self.r.user.get_submitted():
            if submission.saved:
                break
        else:
            self.fail('Could not find saved submission.')
        submission.unsave()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertFalse(submission.saved)

    def test_upvote(self):
        submission = None
        for submission in self.r.user.get_submitted():
            if submission.likes is None:
                break
        else:
            self.fail('Could not find a non-voted submission.')
        submission.upvote()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertEqual(submission.likes, True)


class SubredditTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_attribute_error(self):
        self.assertRaises(AttributeError, getattr, self.subreddit, 'foo')

    def test_get_my_contributions(self):
        for subreddit in self.r.get_my_contributions():
            if text_type(subreddit) == self.sr:
                break
        else:
            self.fail('Could not find contributed reddit in my_contributions.')

    def test_get_my_moderation(self):
        for subreddit in self.r.get_my_moderation():
            if text_type(subreddit) == self.sr:
                break
        else:
            self.fail('Could not find moderated reddit in my_moderation.')

    def test_get_my_subreddits(self):
        for subreddit in self.r.get_my_subreddits():
            # pylint: disable-msg=W0212
            self.assertTrue(text_type(subreddit) in subreddit._info_url)

    @reddit_only
    def test_search(self):
        self.assertTrue(len(list(self.subreddit.search('test'))) > 0)

    def test_subscribe_and_verify(self):
        self.subreddit.subscribe()
        for subreddit in self.r.get_my_subreddits():
            if text_type(subreddit) == self.sr:
                break
        else:
            self.fail('Could not find reddit in my subreddits.')

    def test_subscribe_by_name_and_verify(self):
        self.r.subscribe(self.sr)
        for subreddit in self.r.get_my_subreddits():
            if text_type(subreddit) == self.sr:
                break
        else:
            self.fail('Could not find reddit in my subreddits.')

    def test_unsubscribe_and_verify(self):
        self.subreddit.unsubscribe()
        for subreddit in self.r.get_my_subreddits():
            if text_type(subreddit) == self.sr:
                self.fail('Found reddit in my subreddits.')

    def test_unsubscribe_by_name_and_verify(self):
        self.r.unsubscribe(self.sr)
        for subreddit in self.r.get_my_subreddits():
            if text_type(subreddit) == self.sr:
                self.fail('Found reddit in my subreddits.')


class WikiTests(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_edit_wiki_page(self):
        self.r.login(self.un, '1111')
        page = self.subreddit.get_wiki_page('index')
        content = 'Body: {0}'.format(uuid.uuid4())
        page.edit(content)
        self.disable_cache()
        page = self.subreddit.get_wiki_page('index')
        self.assertEqual(content, page.content_md)

    def test_get_wiki_page(self):
        self.assertEqual(
            '{0}:index'.format(self.sr),
            text_type(self.r.get_wiki_page(self.sr, 'index')))

    def test_get_wiki_pages(self):
        retval = self.subreddit.get_wiki_pages()
        self.assertTrue(len(retval) > 0)
        tmp = self.subreddit.get_wiki_page(retval[0].page).content_md
        self.assertEqual(retval[0].content_md, tmp)


if __name__ == '__main__':
    unittest.main()
