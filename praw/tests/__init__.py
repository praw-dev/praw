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
from six import text_type

from praw import Reddit, decorators, errors, helpers, internal
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
        self.other_non_mod_name = 'PyAPITestUser4'
        self.invalid_user_name = 'PyAPITestInvalid'
        self.un_pswd = '1111'
        self.other_user_pswd = '1111'
        self.other_non_mod_pswd = '1111'

        if self.r.config.is_reddit:
            self.comment_url = self.url('/r/redditdev/comments/dtg4j/')
            self.link_url = self.url('/r/UCSantaBarbara/comments/m77nc/')
            self.link_url_link = 'http://imgur.com/Vr8ZZ'
            self.more_comments_url = self.url('/r/redditdev/comments/dqkfz/')
            self.other_user_id = '6c1xj'
            self.priv_submission_id = '16kbb7'
            self.refresh_token = {
                'edit':            'FFx_0G7Zumyh4AWzIo39bG9KdIM',
                'history':         'j_RKymm8srC3j6cxysYFQZbB4vc',
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

    def first(self, seq, predicate):
        first_hit = next((x for x in seq if predicate(x)), None)
        # Usage of self.assertTrue assumes all inheritance of this Class also
        # inherits from unittest.Testcase
        # pylint: disable-msg=E1101
        self.assertTrue(first_hit is not None)
        return first_hit

    def url(self, path):
        # pylint: disable-msg=W0212
        return urljoin(self.r.config._site_url, path)


class AuthenticatedHelper(BasicHelper):
    def configure(self):
        super(AuthenticatedHelper, self).configure()
        self.r.login(self.un, self.un_pswd)


class AccessControlTests(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()

    def test_exception_get_flair_list_authenticated(self):
        self.r.login(self.un, self.un_pswd)
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
        oth.login(self.other_non_mod_name, self.other_non_mod_pswd)
        self.assertRaises(errors.ModeratorOrScopeRequired,
                          oth.get_settings, self.sr)

    def test_moderator_or_oauth_required_logged_in_from_submission_obj(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login(self.other_non_mod_name, self.other_non_mod_pswd)
        submission = oth.get_submission(url=self.comment_url)
        self.assertRaises(errors.ModeratorOrScopeRequired, submission.remove)

    def test_moderator_or_oauth_required_logged_in_from_subreddit_obj(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login(self.other_non_mod_name, self.other_non_mod_pswd)
        subreddit = oth.get_subreddit(self.sr)
        self.assertRaises(errors.ModeratorOrScopeRequired,
                          subreddit.get_settings)

    def test_moderator_required_multi(self):
        self.r.login(self.un, self.un_pswd)
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
        submission = next(subreddit.get_hot())
        self.assertTrue(subreddit == same_subreddit)
        self.assertFalse(subreddit != same_subreddit)
        self.assertFalse(subreddit == submission)

    def test_get_comments(self):
        num = 50
        result = self.r.get_comments(self.sr, limit=num)
        self.assertEqual(num, len(list(result)))

    def test_get_comments_gilded(self):
        gilded_comments = self.r.get_comments('all', gilded_only=True)
        self.assertTrue(all(comment.gilded > 0 for comment in
                            gilded_comments))

    @reddit_only
    def test_get_controversial(self):
        num = 50
        result = self.r.get_controversial(limit=num, params={'t': 'all'})
        self.assertEqual(num, len(list(result)))

    def test_get_flair_list(self):
        sub = self.r.get_subreddit('python')
        self.assertTrue(next(sub.get_flair_list()))

    def test_get_front_page(self):
        num = 50
        self.assertEqual(num, len(list(self.r.get_front_page(limit=num))))

    def test_get_new(self):
        num = 50
        result = self.r.get_new(limit=num)
        self.assertEqual(num, len(list(result)))

    @reddit_only
    def test_get_new_subreddits(self):
        num = 50
        self.assertEqual(num,
                         len(list(self.r.get_new_subreddits(limit=num))))

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

    def test_get_rising(self):
        # Use low limit as rising listing has few elements. Keeping the limit
        # prevents this test from becoming flaky.
        num = 5
        result = self.r.get_rising(limit=num)
        self.assertEqual(num, len(list(result)))

    def test_get_submissions(self):
        def fullname(url):
            return self.r.get_submission(url).fullname
        fullnames = [fullname(self.comment_url), fullname(self.link_url)] * 100
        retreived = [x.fullname for x in self.r.get_submissions(fullnames)]
        self.assertEqual(fullnames, retreived)

    def test_get_subreddit_recommendations(self):
        result = self.r.get_subreddit_recommendations('python')
        self.assertTrue(result)

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
        self.assertTrue(list(self.r.search('test')))

    @reddit_only
    def test_search_with_syntax(self):
        # Searching with timestamps only possible with cloudsearch
        no_syntax = self.r.search("timestamp:1354348800..1354671600",
                                  subreddit=self.sr)
        self.assertFalse(list(no_syntax))
        with_syntax = self.r.search("timestamp:1354348800..1354671600",
                                    subreddit=self.sr, syntax='cloudsearch')
        self.assertTrue(list(with_syntax))

    @reddit_only
    def test_search_with_time_window(self):
        num = 50
        submissions = len(list(self.r.search('test', subreddit=self.sr,
                                             period='all', limit=num)))
        self.assertTrue(submissions == num)

    def test_search_reddit_names(self):
        self.assertTrue(self.r.search_reddit_names('reddit'))

    def test_store_json_result(self):
        self.r.config.store_json_result = True
        sub = self.r.get_submission(url=self.comment_url)
        self.assertEqual(sub.json_dict['url'], self.comment_url)

    #def test_timeout(self):
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
        submission = next(subreddit.get_top())
        same_submission = self.r.get_submission(submission_id=submission.id)
        if submission.likes:
            submission.downvote()
        else:
            submission.upvote()
        self.assertEqual(submission.likes, same_submission.likes)
        submission.refresh()
        self.assertNotEqual(submission.likes, same_submission.likes)


class EmbedTextTest(unittest.TestCase):
    embed_text = "Hello"

    def test_no_docstring(self):
        # pylint: disable-msg=W0212
        new_doc = decorators._embed_text(None, self.embed_text)
        self.assertEqual(new_doc, self.embed_text)

    def test_one_liner(self):
        # pylint: disable-msg=W0212
        new_doc = decorators._embed_text("Returns something cool",
                                         self.embed_text)
        self.assertEqual(new_doc,
                         "Returns something cool\n\n" + self.embed_text)

    def test_multi_liner(self):
        doc = """Jiggers the bar

              Only run if foo is instantiated.

              """
        # pylint: disable-msg=W0212
        new_doc = decorators._embed_text(doc, self.embed_text)
        self.assertEqual(new_doc, doc + self.embed_text + "\n\n")

    def test_single_plus_params(self):
        doc = """Jiggers the bar

              :params foo: Self explanatory.

              """
        expected_doc = """Jiggers the bar

              {}

              :params foo: Self explanatory.

              """.format(self.embed_text)
        # pylint: disable-msg=W0212
        new_doc = decorators._embed_text(doc, self.embed_text)
        self.assertEqual(new_doc, expected_doc)

    def test_multi_plus_params(self):
        doc = """Jiggers the bar

              Jolly importment.

              :params foo: Self explanatory.
              :returns: The jiggered bar.

              """
        expected_doc = """Jiggers the bar

              Jolly importment.

              {}

              :params foo: Self explanatory.
              :returns: The jiggered bar.

              """.format(self.embed_text)
        # pylint: disable-msg=W0212
        new_doc = decorators._embed_text(doc, self.embed_text)
        self.assertEqual(new_doc, expected_doc)

    def test_additional_params(self):
        doc = """Jiggers the bar

              Jolly important.

              :params foo: Self explanatory.
              :returns: The jiggered bar.

              The additional parameters are passed directly into
              :meth:`.get_content`. Note: the `url` parameter cannot be
              altered.

              """
        expected_doc = """Jiggers the bar

              Jolly important.

              {}

              :params foo: Self explanatory.
              :returns: The jiggered bar.

              The additional parameters are passed directly into
              :meth:`.get_content`. Note: the `url` parameter cannot be
              altered.

              """.format(self.embed_text)
        # pylint: disable-msg=W0212
        new_doc = decorators._embed_text(doc, self.embed_text)
        self.assertEqual(new_doc, expected_doc)


class EncodingTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_author_encoding(self):
        # pylint: disable-msg=E1101
        a1 = next(self.r.get_new()).author
        a2 = self.r.get_redditor(text_type(a1))
        self.assertEqual(a1, a2)
        s1 = next(a1.get_submitted())
        s2 = next(a2.get_submitted())
        self.assertEqual(s1, s2)

    def test_unicode_comment(self):
        sub = next(self.r.get_subreddit(self.sr).get_new())
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
        predicate = lambda item: isinstance(item, MoreComments)
        item = self.first(self.submission.comments, predicate)
        self.assertTrue(item.comments())


class CommentEditTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_reply(self):
        comment = next(self.r.user.get_comments())
        new_body = '%s\n\n+Edit Text' % comment.body
        comment = comment.edit(new_body)
        self.assertEqual(comment.body, new_body)


class CommentPermalinkTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_inbox_permalink(self):
        predicate = lambda item: isinstance(item, Comment)
        item = self.first(self.r.get_inbox(), predicate)
        self.assertTrue(item.id in item.permalink)

    def test_user_comments_permalink(self):
        item = next(self.r.user.get_comments())
        self.assertTrue(item.id in item.permalink)

    def test_get_comments_permalink(self):
        sub = self.r.get_subreddit(self.sr)
        item = next(sub.get_comments())
        self.assertTrue(item.id in item.permalink)


class CommentReplyTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_add_comment_and_verify(self):
        text = 'Unique comment: %s' % uuid.uuid4()
        # pylint: disable-msg=E1101
        submission = next(self.subreddit.get_new())
        # pylint: enable-msg=E1101
        comment = submission.add_comment(text)
        self.assertEqual(comment.submission, submission)
        self.assertEqual(comment.body, text)

    def test_add_reply_and_verify(self):
        text = 'Unique reply: %s' % uuid.uuid4()
        predicate = lambda submission: submission.num_comments > 0
        submission = self.first(self.subreddit.get_new(), predicate)
        comment = submission.comments[0]
        reply = comment.reply(text)
        self.assertEqual(reply.parent_id, comment.fullname)
        self.assertEqual(reply.body, text)


class CommentReplyNoneTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_front_page_comment_replies_are_none(self):
        # pylint: disable-msg=E1101,W0212
        item = next(self.r.get_comments('all'))
        self.assertEqual(item._replies, None)

    def test_inbox_comment_replies_are_none(self):
        predicate = lambda item: isinstance(item, Comment)
        comment = self.first(self.r.get_inbox(), predicate)
        # pylint: disable-msg=W0212
        self.assertEqual(comment._replies, None)

    def test_spambox_comments_replies_are_none(self):
        predicate = lambda item: isinstance(item, Comment)
        sequence = self.r.get_subreddit(self.sr).get_spam()
        comment = self.first(sequence, predicate)
        # pylint: disable-msg=W0212
        self.assertEqual(comment._replies, None)

    def test_user_comment_replies_are_none(self):
        predicate = lambda item: isinstance(item, Comment)
        comment = self.first(self.r.user.get_comments(), predicate)
        # pylint: disable-msg=W0212
        self.assertEqual(comment._replies, None)


class FlairTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_add_link_flair(self):
        flair_text = 'Flair: %s' % uuid.uuid4()
        sub = next(self.subreddit.get_new())
        self.subreddit.set_flair(sub, flair_text)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_text)

    def test_add_link_flair_through_submission(self):
        flair_text = 'Flair: %s' % uuid.uuid4()
        sub = next(self.subreddit.get_new())
        sub.set_flair(flair_text)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_text)

    def test_add_link_flair_to_invalid_subreddit(self):
        sub = next(self.r.get_subreddit('python').get_new())
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
                         {'user': self.un, 'flair_css_class': 'xx'},
                         {'user': self.other_user_name,
                          'flair_text': 'AWESOME',
                          'flair_css_class': 'css'}]
        self.subreddit.set_flair_csv(flair_mapping)
        self.assertEqual([], flair_diff(flair_mapping,
                                        list(self.subreddit.get_flair_list())))

    def test_flair_csv_many(self):
        users = ('reddit', self.un, self.other_user_name)
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
                         {'user': self.other_user_name, 'flair_css_class':
                          'blah'}]
        self.subreddit.set_flair_csv(flair_mapping)

    def test_flair_csv_empty(self):
        self.assertRaises(errors.ClientException,
                          self.subreddit.set_flair_csv, [])

    def test_flair_csv_requires_user(self):
        flair_mapping = [{'flair_text': 'hsdf'}]
        self.assertRaises(errors.ClientException,
                          self.subreddit.set_flair_csv, flair_mapping)


class FlairSelectTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.priv_sr)
        self.user_flair_templates = {
            'UserCssClassOne':  ('21e00aae-09cf-11e3-a4f1-12313d281541',
                                 'default_user_flair_text_one'),
            'UserCssClassTwo':  ('2f6504c2-09cf-11e3-9d8d-12313d281541',
                                 'default_user_flair_text_two')
        }
        self.link_flair_templates = {
            'LinkCssClassOne':  ('36a573c0-09cf-11e3-b5f7-12313d096169',
                                 'default_link_flair_text_one'),
            'LinkCssClassTwo':  ('3b73f516-09cf-11e3-9a71-12313d281541',
                                 'default_link_flair_text_two')
        }

    def get_different_user_flair_class(self):
        flair = self.r.get_flair(self.subreddit, self.r.user)
        if flair == self.user_flair_templates.keys()[0]:
            different_flair = self.user_flair_templates.keys()[1]
        else:
            different_flair = self.user_flair_templates.keys()[0]
        return different_flair

    def get_different_link_flair_class(self, submission):
        flair = submission.link_flair_css_class
        if flair == self.link_flair_templates.keys()[0]:
            different_flair = self.link_flair_templates.keys()[1]
        else:
            different_flair = self.link_flair_templates.keys()[0]
        return different_flair

    def test_select_user_flair(self):
        flair_class = self.get_different_user_flair_class()
        flair_id = self.user_flair_templates[flair_class][0]
        flair_default_text = self.user_flair_templates[flair_class][1]
        self.r.select_flair(item=self.subreddit,
                            flair_template_id=flair_id)
        flair = self.r.get_flair(self.subreddit, self.r.user)
        self.assertEqual(flair['flair_text'], flair_default_text)
        self.assertEqual(flair['flair_css_class'], flair_class)

    def test_select_link_flair(self):
        sub = next(self.subreddit.get_new())
        flair_class = self.get_different_link_flair_class(sub)
        flair_id = self.link_flair_templates[flair_class][0]
        flair_default_text = self.link_flair_templates[flair_class][1]
        self.r.select_flair(item=sub,
                            flair_template_id=flair_id)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_default_text)
        self.assertEqual(sub.link_flair_css_class, flair_class)

    def test_select_user_flair_custom_text(self):
        flair_class = self.get_different_user_flair_class()
        flair_id = self.user_flair_templates[flair_class][0]
        flair_text = 'Flair: %s' % uuid.uuid4()
        self.r.select_flair(item=self.subreddit,
                            flair_template_id=flair_id,
                            flair_text=flair_text)
        flair = self.r.get_flair(self.subreddit, self.r.user)
        self.assertEqual(flair['flair_text'], flair_text)
        self.assertEqual(flair['flair_css_class'], flair_class)

    def test_select_link_flair_custom_text(self):
        sub = next(self.subreddit.get_new())
        flair_class = self.get_different_link_flair_class(sub)
        flair_id = self.link_flair_templates[flair_class][0]
        flair_text = 'Flair: %s' % uuid.uuid4()
        self.r.select_flair(item=sub,
                            flair_template_id=flair_id,
                            flair_text=flair_text)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_text)
        self.assertEqual(sub.link_flair_css_class, flair_class)

    def test_select_user_flair_remove(self):
        flair = self.r.get_flair(self.subreddit, self.r.user)
        if flair['flair_css_class'] is None:
            flair_class = self.get_different_user_flair_class()
            flair_id = self.user_flair_templates[flair_class][0]
            self.r.select_flair(item=self.subreddit,
                                flair_template_id=flair_id)
        self.r.select_flair(item=self.subreddit)
        flair = self.r.get_flair(self.subreddit, self.r.user)
        self.assertEqual(flair['flair_text'], None)
        self.assertEqual(flair['flair_css_class'], None)

    def test_select_link_flair_remove(self):
        sub = next(self.subreddit.get_new())
        if sub.link_flair_css_class is None:
            flair_class = self.get_different_link_flair_class(sub)
            flair_id = self.link_flair_templates[flair_class][0]
            self.r.select_flair(item=sub,
                                flair_template_id=flair_id)
        self.r.select_flair(item=sub)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, None)
        self.assertEqual(sub.link_flair_css_class, None)


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
        self.assertRaises(errors.BadCSSName,
                          self.subreddit.delete_image, 'invalid_image_name')

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
        self.assertTrue(any(name in text_type(x['name']) for x in images_json))

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
        self.assertTrue(any(name in text_type(x['name']) for x in images_json))


class LocalOnlyTest(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()

    @local_only
    def test_create_existing_redditor(self):
        self.r.login(self.un, self.un_pswd)
        self.assertRaises(errors.UsernameExists, self.r.create_redditor,
                          self.other_user_name, self.other_user_pswd)

    @local_only
    def test_create_existing_subreddit(self):
        self.r.login(self.un, self.un_pswd)
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
        self.r.login(self.un, self.un_pswd)
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
        self.r.login(self.other_user_name, self.other_user_pswd)
        self.assertTrue(self.r.user.has_mail)
        self.r.get_unread(limit=1, unset_has_mail=True, update_user=True)
        self.assertFalse(self.r.user.has_mail)

    def test_mark_as_read(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login(self.other_user_name, self.other_user_pswd)
        # pylint: disable-msg=E1101
        msg = next(oth.get_unread(limit=1))
        msg.mark_as_read()
        self.assertTrue(msg not in oth.get_unread(limit=5))

    def test_mark_as_unread(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login(self.other_user_name, self.other_user_pswd)
        msg = self.first(oth.get_inbox(), lambda msg: not msg.new)
        msg.mark_as_unread()
        self.assertTrue(msg in oth.get_unread())

    def test_mark_multiple_as_read(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login(self.other_user_name, self.other_user_pswd)
        messages = []
        for msg in oth.get_unread(limit=None):
            if msg.author != oth.user.name:
                messages.append(msg)
                if len(messages) >= 2:
                    break
        self.assertEqual(2, len(messages))
        oth.user.mark_as_read(messages)
        unread = list(oth.get_unread(limit=5))
        self.assertTrue(all(msg not in unread for msg in messages))

    def test_reply_to_message_and_verify(self):
        text = 'Unique message reply: %s' % uuid.uuid4()
        predicate = lambda msg: (isinstance(msg, Message)
                                 and msg.author == self.r.user)
        msg = self.first(self.r.get_inbox(), predicate)
        reply = msg.reply(text)
        self.assertEqual(reply.parent_id, msg.fullname)

    def test_send(self):
        subject = 'Unique message: %s' % uuid.uuid4()
        self.r.user.send_message(subject, 'Message content')
        self.first(self.r.get_inbox(), lambda msg: msg.subject == subject)

    def test_send_invalid(self):
        subject = 'Unique message: %s' % uuid.uuid4()
        self.assertRaises(errors.InvalidUser, self.r.send_message,
                          self.invalid_user_name, subject, 'Message content')


class ModeratorSubmissionTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_approve(self):
        submission = next(self.subreddit.get_spam())
        if not submission:
            self.fail('Could not find a submission to approve.')
        submission.approve()
        predicate = lambda approved: approved.id == submission.id
        self.first(self.subreddit.get_new(), predicate)

    def test_ignore_reports(self):
        submission = next(self.subreddit.get_new())
        self.assertFalse(submission in self.subreddit.get_mod_log())
        submission.ignore_reports()
        submission.report()
        self.disable_cache()
        submission.refresh()
        self.assertFalse(submission in self.subreddit.get_mod_log())
        self.assertTrue(submission.num_reports > 0)

    def test_remove(self):
        submission = next(self.subreddit.get_new())
        if not submission:
            self.fail('Could not find a submission to remove.')
        submission.remove()
        predicate = lambda removed: removed.id == submission.id
        self.first(self.subreddit.get_spam(), predicate)


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

    def test_mod_mail_send(self):
        subject = 'Unique message: %s' % uuid.uuid4()
        self.r.get_subreddit(self.sr).send_message(subject, 'Content')
        self.first(self.r.get_mod_mail(), lambda msg: msg.subject == subject)

    def test_get_mod_queue(self):
        self.assertTrue(list(self.r.get_subreddit('mod').get_mod_queue()))

    def test_get_mod_queue_with_default_subreddit(self):
        self.assertTrue(list(self.r.get_mod_queue()))

    def test_get_mod_queue_multi(self):
        multi = '{0}+{1}'.format(self.sr, self.priv_sr)
        self.assertTrue(list(self.r.get_subreddit(multi).get_mod_queue()))

    def test_get_unmoderated(self):
        self.assertTrue(list(self.subreddit.get_unmoderated()))


class ModeratorUserTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)
        self.other = self.r.get_redditor(self.other_user_name, fetch=True)

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
        self.r.login(self.other_user_name, self.other_user_pswd)
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
            tmp.login(self.other_user_name, self.other_user_pswd)
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
    def test_scope_history(self):
        self.r.refresh_access_information(self.refresh_token['history'])
        self.assertTrue(list(self.r.get_redditor(self.un).get_liked()))

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
        num = 50
        self.r.refresh_access_information(self.refresh_token['modlog'])
        result = self.r.get_subreddit(self.sr).get_mod_log(limit=num)
        self.assertEqual(num, len(list(result)))

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
        self.assertTrue(list(subreddit.get_top()))

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
        self.assertTrue(list(self.r.get_comments(self.priv_sr)))

    @reddit_only
    def test_scope_read_priv_sub_comments(self):
        self.r.refresh_access_information(self.refresh_token['read'])
        submission = Submission.from_id(self.r, self.priv_submission_id)
        self.assertTrue(submission.comments)

    @reddit_only
    def test_scope_submit(self):
        self.r.refresh_access_information(self.refresh_token['submit'])
        result = self.r.submit(self.sr, 'OAuth Submit', text='Foo')
        self.assertTrue(isinstance(result, Submission))

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
        result = self.r.refresh_access_information(
            self.refresh_token['identity'], update_session=False)
        self.assertTrue(self.r.user is None)
        self.r.set_access_credentials(**result)
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

    def test_duplicate_login(self):
        self.r.login(self.other_user_name, self.other_user_pswd)

    def test_get_disliked(self):
        # Pulls from get_liked. Problem here may come from get_liked
        item = next(self.r.user.get_liked())
        item.downvote()
        self.delay()  # The queue needs to be processed
        self.assertFalse(item in self.r.user.get_liked())

    def test_get_friends(self):
        # See issue 175.
        # If this test fails and doesn't raise an exception, but smoothly calls
        # self.r.user.get_friends, then issue 175 has been resolved.
        self.assertRaises(errors.RedirectException, self.r.user.get_friends)

    def test_get_hidden(self):
        submission = next(self.r.user.get_submitted())
        submission.hide()
        self.delay()  # The queue needs to be processed
        item = next(self.r.user.get_hidden())
        item.unhide()
        self.delay()
        self.assertFalse(item in self.r.user.get_hidden())

    def test_get_liked(self):
        # Pulls from get_disliked. Problem here may come from get_disliked
        item = next(self.r.user.get_disliked())
        item.upvote()
        self.delay()  # The queue needs to be processed
        self.assertFalse(item in self.r.user.get_disliked())

    def test_get_redditor(self):
        self.assertEqual(self.other_user_id, self.other_user.id)

    def test_get_submitted(self):
        redditor = self.r.get_redditor(self.other_non_mod_name)
        self.assertTrue(list(redditor.get_submitted()))

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

    def test_set_stylesheet_invalid_css(self):
        self.assertRaises(errors.BadCSS, self.subreddit.set_stylesheet,
                          'INVALID CSS')

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
        predicate = lambda item: not item.is_self
        found = self.first(self.r.user.get_submitted(), predicate)
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
        sub_id = self.submission_edit_id
        submission = self.r.get_submission(submission_id=sub_id)
        if submission.distinguished:
            verify_undistinguish(submission)
            verify_distinguish(submission)
        else:
            verify_distinguish(submission)
            verify_undistinguish(submission)

    def test_edit_link(self):
        predicate = lambda item: not item.is_self
        found = self.first(self.r.user.get_submitted(), predicate)
        self.assertRaises(HTTPError, found.edit, 'text')

    def test_edit_self(self):
        predicate = lambda item: item.is_self
        found = self.first(self.r.user.get_submitted(), predicate)
        new_body = '%s\n\n+Edit Text' % found.selftext
        found = found.edit(new_body)
        self.assertEqual(found.selftext, new_body)

    def test_mark_as_nsfw_as_author(self):
        self.disable_cache()
        self.r.login(self.other_non_mod_name, self.other_non_mod_pswd)
        submission = self.r.get_submission(submission_id="1nt8co")
        self.assertEqual(submission.author, self.r.user)
        originally_nsfw = submission.over_18
        if originally_nsfw:
            submission.unmark_as_nsfw()
        else:
            submission.mark_as_nsfw()
        submission.refresh()
        self.assertNotEqual(originally_nsfw, submission.over_18)

    def test_mark_as_nsfw_as_mod(self):
        self.disable_cache()
        submission = self.r.get_submission(submission_id="1nt8co")
        submission.mark_as_nsfw()
        submission.refresh()
        self.assertTrue(submission.over_18)

    def test_mark_as_nsfw_exception(self):
        self.disable_cache()
        self.r.login(self.other_non_mod_name, self.other_non_mod_pswd)
        predicate = lambda item: item.author != self.r.user
        found = self.first(self.subreddit.get_top(), predicate)
        self.assertRaises(errors.ModeratorOrScopeRequired, found.mark_as_nsfw)

    def test_unmark_as_nsfw(self):
        self.disable_cache()
        submission = self.r.get_submission(submission_id="1nt8co")
        submission.unmark_as_nsfw()
        submission.refresh()
        self.assertFalse(submission.over_18)


class SubmissionTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_clear_vote(self):
        predicate = lambda submission: submission.likes is False
        submission = self.first(self.r.user.get_submitted(), predicate)
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
        predicate = lambda submission: submission.likes is True
        submission = self.first(self.r.user.get_submitted(), predicate)
        submission.downvote()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertEqual(submission.likes, False)

    def test_hide(self):
        self.disable_cache()
        predicate = lambda item: not item.hidden
        submission = self.first(self.r.user.get_submitted(), predicate)
        submission.hide()
        submission.refresh()
        self.assertTrue(submission.hidden)

    def test_report(self):
        self.disable_cache()
        # login as new user to report submission
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login(self.other_user_name, self.other_user_pswd)
        subreddit = oth.get_subreddit(self.sr)
        predicate = lambda submission: not submission.hidden
        submission = self.first(subreddit.get_new(), predicate)
        submission.report()
        # check if submission was reported
        predicate = lambda report: report.id == submission.id
        self.first(self.r.get_subreddit(self.sr).get_reports(), predicate)

    def test_save(self):
        predicate = lambda submission: not submission.saved
        submission = self.first(self.r.user.get_submitted(), predicate)
        submission.save()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertTrue(submission.saved)
        # verify in saved_links
        self.first(self.r.user.get_saved(), lambda item: item == submission)

    def test_short_link(self):
        submission = next(self.r.get_new())
        if self.r.config.is_reddit:
            self.assertTrue(submission.id in submission.short_link)
        else:
            self.assertRaises(errors.ClientException, getattr, submission,
                              'short_link')

    def test_sticky_unsticky(self):
        def verify_sticky():
            submission.sticky()
            submission.refresh()
            self.assertTrue(submission.stickied)

        def verify_unsticky():
            submission.unsticky()
            submission.refresh()
            self.assertFalse(submission.stickied)

        self.disable_cache()
        submission_id = self.submission_edit_id
        submission = self.r.get_submission(submission_id=submission_id)

        if submission.stickied:
            verify_unsticky()
            verify_sticky()
        else:
            verify_sticky()
            verify_unsticky()

    def test_unhide(self):
        self.disable_cache()
        predicate = lambda submission: submission.hidden
        submission = self.first(self.r.user.get_submitted(), predicate)
        submission.unhide()
        submission.refresh()
        self.assertFalse(submission.hidden)

    def test_unsave(self):
        predicate = lambda submission: submission.saved
        submission = self.first(self.r.user.get_submitted(), predicate)
        submission.unsave()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertFalse(submission.saved)

    def test_upvote(self):
        predicate = lambda submission: submission.likes is None
        submission = self.first(self.r.user.get_submitted(), predicate)
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

    def test_get_contributors_private(self):
        self.r.login(self.other_non_mod_name, self.other_non_mod_pswd)
        private_sub = self.r.get_subreddit(self.priv_sr)
        self.assertTrue(list(private_sub.get_contributors()))

    def test_get_contributors_public(self):
        self.assertTrue(list(self.subreddit.get_contributors()))

    def test_get_contributors_public_exception(self):
        self.r.login(self.other_non_mod_name, self.other_non_mod_pswd)
        self.assertRaises(errors.ModeratorRequired,
                          self.subreddit.get_contributors)

    def test_get_my_contributions(self):
        predicate = lambda subreddit: text_type(subreddit) == self.sr
        self.first(self.r.get_my_contributions(), predicate)

    def test_get_my_moderation(self):
        predicate = lambda subreddit: text_type(subreddit) == self.sr
        self.first(self.r.get_my_moderation(), predicate)

    def test_get_my_subreddits(self):
        for subreddit in self.r.get_my_subreddits():
            # pylint: disable-msg=W0212
            self.assertTrue(text_type(subreddit) in subreddit._info_url)

    @reddit_only
    def test_search(self):
        self.assertTrue(list(self.subreddit.search('test')))

    def test_subscribe_and_verify(self):
        self.subreddit.subscribe()
        predicate = lambda subreddit: text_type(subreddit) == self.sr
        self.first(self.r.get_my_subreddits(), predicate)

    def test_subscribe_by_name_and_verify(self):
        self.r.subscribe(self.sr)
        predicate = lambda subreddit: text_type(subreddit) == self.sr
        self.first(self.r.get_my_subreddits(), predicate)

    def test_unsubscribe_and_verify(self):
        self.subreddit.unsubscribe()
        pred = lambda subreddit: text_type(subreddit) != self.sr
        self.assertTrue(all(pred(sub) for sub in self.r.get_my_subreddits()))

    def test_unsubscribe_by_name_and_verify(self):
        self.r.unsubscribe(self.sr)
        pred = lambda subreddit: text_type(subreddit) != self.sr
        self.assertTrue(all(pred(sub) for sub in self.r.get_my_subreddits()))


class ToRedditListTest(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()

    def test__to_reddit_list(self):
        # pylint: disable-msg=W0212
        output = internal._to_reddit_list('hello')
        self.assertEquals('hello', output)

    def test__to_reddit_list_with_list(self):
        # pylint: disable-msg=W0212
        output = internal._to_reddit_list(['hello'])
        self.assertEqual('hello', output)

    def test__to_reddit_list_with_empty_list(self):
        # pylint: disable-msg=W0212
        output = internal._to_reddit_list([])
        self.assertEqual('', output)

    def test__to_reddit_list_with_big_list(self):
        # pylint: disable-msg=W0212
        output = internal._to_reddit_list(['hello', 'world'])
        self.assertEqual('hello,world', output)

    def test__to_reddit_list_with_object(self):
        obj = self.r.get_subreddit(self.sr)
        # pylint: disable-msg=W0212
        output = internal._to_reddit_list(obj)
        self.assertEqual(self.sr, output)

    def test__to_reddit_list_with_object_in_list(self):
        obj = self.r.get_subreddit(self.sr)
        # pylint: disable-msg=W0212
        output = internal._to_reddit_list([obj])
        self.assertEqual(self.sr, output)

    def test__to_reddit_list_with_mix(self):
        obj = self.r.get_subreddit(self.sr)
        # pylint: disable-msg=W0212
        output = internal._to_reddit_list([obj, 'hello'])
        self.assertEqual("{0},{1}".format(self.sr, 'hello'), output)


class WikiTests(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_edit_wiki_page(self):
        self.r.login(self.un, self.un_pswd)
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
        result = self.subreddit.get_wiki_pages()
        self.assertTrue(result)
        tmp = self.subreddit.get_wiki_page(result[0].page).content_md
        self.assertEqual(result[0].content_md, tmp)


if __name__ == '__main__':
    unittest.main()
