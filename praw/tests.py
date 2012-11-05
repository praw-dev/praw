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

from __future__ import unicode_literals

import random
import time
import unittest
import uuid
import warnings
from six import advance_iterator as six_next, text_type

from praw import Reddit, errors, helpers
from praw.compat import (HTTPError, URLError,  # pylint: disable-msg=E0611
                         urljoin)
from praw.objects import Comment, LoggedInRedditor, Message, MoreComments

USER_AGENT = 'PRAW_test_suite'


def flair_diff(root, other):
    """Function for comparing two flairlists supporting optional arguments."""
    keys = ['user', 'flair_text', 'flair_css_class']
    root_items = set(tuple(item[key].lower() if key in item and item[key] else
                           '' for key in keys) for item in root)
    other_items = set(tuple(item[key].lower() if key in item and item[key] else
                            '' for key in keys) for item in other)
    return list(root_items - other_items)


class BasicHelper(object):
    def configure(self):
        self.r = Reddit(USER_AGENT)
        self.sr = 'reddit_api_test'
        self.un = 'PyApiTestUser2'
        self.other_user_name = 'PyApiTestUser3'

        if self.r.config.is_reddit:
            self.comment_url = self.url('r/redditdev/comments/dtg4j/')
            self.link_url = self.url('/r/UCSantaBarbara/comments/m77nc/')
            self.link_url_link = 'http://imgur.com/Vr8ZZ'
            self.more_comments_url = self.url('/r/redditdev/comments/dqkfz/')
            self.other_user_id = '6c1xj'
        else:
            self.comment_url = self.url('/r/reddit_test6/comments/y/')
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


class BasicTest(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()

    def test_comments_contains_no_noncomment_objects(self):
        comments = self.r.get_submission(url=self.comment_url).comments
        self.assertFalse([item for item in comments if not
                          (isinstance(item, Comment) or
                           isinstance(item, MoreComments))])

    def test_equality(self):
        subreddit = self.r.get_subreddit(self.sr)
        same_subreddit = self.r.get_subreddit(self.sr)
        submission = six_next(subreddit.get_hot())
        self.assertTrue(subreddit == same_subreddit)
        self.assertFalse(subreddit != same_subreddit)
        self.assertFalse(subreddit == submission)

    def test_get_all_comments(self):
        num = 50
        self.assertEqual(num, len(list(self.r.get_all_comments(limit=num))))

    def test_get_controversial(self):
        num = 50
        result = self.r.get_controversial(limit=num, url_data={'t': 'all'})
        self.assertEqual(num, len(list(result)))

    def test_get_front_page(self):
        num = 50
        self.assertEqual(num, len(list(self.r.get_front_page(limit=num))))

    def test_get_new(self):
        num = 50
        result = self.r.get_new(limit=num, url_data={'sort': 'new'})
        self.assertEqual(num, len(list(result)))

    def test_get_popular_reddits(self):
        num = 50
        self.assertEqual(num, len(list(self.r.get_popular_reddits(limit=num))))

    def test_get_top(self):
        num = 50
        result = self.r.get_top(limit=num, url_data={'t': 'all'})
        self.assertEqual(num, len(list(result)))

    def test_flair_list(self):
        sub = self.r.get_subreddit('python')
        self.assertTrue(six_next(sub.flair_list()))

    def test_info_by_known_url_returns_known_id_link_post(self):
        found_links = self.r.info(self.link_url_link)
        tmp = self.r.get_submission(url=self.link_url)
        self.assertTrue(tmp in found_links)

    def test_info_by_self_url_raises_warning(self):
        url = six_next(self.r.get_new(url_data={'sort': 'new'})).permalink
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            self.r.info(url)
            self.assertEqual(len(w), 1)
            self.assertEqual(w[0].category, UserWarning)
            self.assertTrue('self' in text_type(w[0].message))

    def test_info_by_url_also_found_by_id(self):
        # pylint: disable-msg=E1101
        found_link = six_next(self.r.info(self.link_url_link))
        found_by_id = self.r.info(thing_id=found_link.content_id)
        self.assertTrue(found_by_id)
        self.assertTrue(found_link in found_by_id)

    def test_is_username_available(self):
        self.assertFalse(self.r.is_username_available('_Daimon_'))
        self.assertTrue(self.r.is_username_available('_Daimon__'))
        self.assertFalse(self.r.is_username_available(''))

    def test_not_logged_in_submit(self):
        self.assertRaises(errors.LoginRequired, self.r.submit,
                          self.sr, 'TITLE', text='BODY')

    def test_not_logged_in_when_initialized(self):
        self.assertEqual(self.r.user, None)

    def test_require_user_agent(self):
        self.assertRaises(TypeError, Reddit, user_agent=None)
        self.assertRaises(TypeError, Reddit, user_agent='')
        self.assertRaises(TypeError, Reddit, user_agent=1)

    def test_search(self):
        if not self.r.config.is_reddit:
            raise Exception('Search does not work locally.')
        self.assertTrue(len(list(self.r.search('test'))) > 0)

    def test_search_reddit_names(self):
        self.assertTrue(len(self.r.search_reddit_names('reddit')) > 0)

    def test_timeout(self):
        # pylint: disable-msg=W0212
        from socket import timeout
        try:
            helpers._request(self.r, self.r.config['comments'], timeout=0.001)
        except URLError as error:
            self.assertEqual(text_type(error.reason), 'timed out')
        except timeout:
            pass
        else:
            self.fail('Timeout did not raise the proper exception.')


class CacheTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_cache(self):
        subreddit = self.r.get_subreddit(self.sr)
        title = 'Test Cache: %s' % uuid.uuid4()
        body = "BODY"
        original_listing = list(subreddit.get_new_by_date(limit=5))
        subreddit.submit(title, body)
        new_listing = list(subreddit.get_new_by_date(limit=5))
        self.assertEqual(original_listing, new_listing)
        self.disable_cache()
        no_cache_listing = list(subreddit.get_new_by_date(limit=5))
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

    def test_users_share_cache(self):
        subreddit = self.r.get_subreddit(self.sr)
        title = 'Test User Sharing Of Cache: %s' % uuid.uuid4()
        body = "BODY"
        original_listing = list(subreddit.get_new_by_date(limit=5))
        subreddit.submit(title, body)
        self.r.login('PyApiTestUser2', '1111')
        new_user_listing = list(subreddit.get_new_by_date(limit=5))
        self.assertEqual(original_listing, new_user_listing)


class EncodingTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_author_encoding(self):
        # pylint: disable-msg=E1101
        a1 = six_next(self.r.get_new(url_data={'sort': 'new'})).author
        a2 = self.r.get_redditor(text_type(a1))
        self.assertEqual(a1, a2)
        s1 = six_next(a1.get_submitted())
        s2 = six_next(a2.get_submitted())
        self.assertEqual(s1, s2)

    def test_unicode_comment(self):
        sub = six_next(self.r.get_subreddit(self.sr).get_new_by_date())
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
        self.r.config.comment_limit = 10
        self.submission = self.r.get_submission(url=self.more_comments_url)

    def test_all_comments(self):
        c_len = len(self.submission.comments)
        cf_len = len(self.submission.comments_flat)
        ac_len = len(self.submission.all_comments)
        acf_len = len(self.submission.all_comments_flat)

        # pylint: disable-msg=W0212
        self.assertEqual(len(self.submission._comments_by_id), acf_len)
        self.assertTrue(c_len < ac_len)
        self.assertTrue(c_len < cf_len)
        self.assertTrue(ac_len < acf_len)
        self.assertTrue(cf_len < acf_len)


class CommentAttributeTest(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()
        self.submission = self.r.get_submission(url=self.comment_url)

    def test_all_comments(self):
        self.assertTrue(len(self.submission.all_comments))

    def test_all_comments_flat(self):
        self.assertTrue(len(self.submission.all_comments_flat))

    def test_comments(self):
        self.assertTrue(len(self.submission.comments))

    def test_comments_flat(self):
        self.assertTrue(len(self.submission.comments_flat))

    def test_comments_score(self):
        comment = self.submission.comments[0]
        self.assertEqual(comment.ups - comment.downs, comment.score)


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
        for item in self.r.user.get_inbox():
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
        submission = six_next(self.subreddit.get_new_by_date())
        # pylint: enable-msg=E1101
        comment = submission.add_comment(text)
        self.assertEqual(comment.submission, submission)
        self.assertEqual(comment.body, text)

    def test_add_reply_and_verify(self):
        text = 'Unique reply: %s' % uuid.uuid4()
        found = None
        for submission in self.subreddit.get_new_by_date():
            if submission.num_comments > 0:
                found = submission
                break
        else:
            self.fail('Could not find a submission with comments.')
        comment = found.comments[0]
        reply = comment.reply(text)
        self.assertEqual(reply.parent_id, comment.content_id)
        self.assertEqual(reply.body, text)


class CommentReplyNoneTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_front_page_comment_replies_are_none(self):
        # pylint: disable-msg=E1101,W0212
        item = six_next(self.r.get_all_comments())
        self.assertEqual(item._replies, None)

    def test_inbox_comment_replies_are_none(self):
        for item in self.r.user.get_inbox():
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


class SettingsTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_set_settings(self):
        title = 'Reddit API Test %s' % uuid.uuid4()
        self.subreddit.set_settings(title)
        self.assertEqual(self.subreddit.get_settings()['title'], title)

    def test_set_settings_none_values(self):
        title = 'Reddit API Test %s' % uuid.uuid4()
        self.subreddit.set_settings(title, wiki_edit_age=None,
                                    wiki_edit_karma=None)
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


class FlairTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_add_link_flair(self):
        flair_text = 'Flair: %s' % uuid.uuid4()
        sub = six_next(self.subreddit.get_new_by_date())
        self.subreddit.set_flair(sub, flair_text)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_text)

    def test_add_link_flair_through_submission(self):
        flair_text = 'Falir: %s' % uuid.uuid4()
        sub = six_next(self.subreddit.get_new_by_date())
        sub.set_flair(flair_text)
        sub = self.r.get_submission(sub.permalink)
        self.assertEqual(sub.link_flair_text, flair_text)

    def test_add_link_flair_to_invalid_subreddit(self):
        sub = six_next(self.r.get_subreddit('python').get_new_by_date())
        self.assertRaises(HTTPError, self.subreddit.set_flair, sub, 'text')

    def test_add_user_flair_by_subreddit_name(self):
        flair_text = 'Flair: %s' % uuid.uuid4()
        self.r.set_flair(self.sr, self.r.user, flair_text)
        flair = self.r.get_flair(self.sr, self.r.user)
        self.assertEqual(flair['flair_text'], flair_text)
        self.assertEqual(flair['flair_css_class'], None)

    def test_add_user_flair_to_invalid_user(self):
        self.assertRaises(errors.APIException, self.subreddit.set_flair, 'b')

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

    def test_flair_csv_and_flair_list(self):
        # Clear all flair
        self.subreddit.clear_all_flair()
        self.delay(5)  # Wait for flair to clear
        self.assertEqual([], list(self.subreddit.flair_list()))

        # Set flair
        flair_mapping = [{'user': 'reddit', 'flair_text': 'dev'},
                         {'user': 'PyAPITestUser2', 'flair_css_class': 'xx'},
                         {'user': 'PyAPITestUser3', 'flair_text': 'AWESOME',
                          'flair_css_class': 'css'}]
        self.subreddit.set_flair_csv(flair_mapping)
        self.assertEqual([], flair_diff(flair_mapping,
                                        list(self.subreddit.flair_list())))

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


class LocalOnlyTest(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()
        if self.r.config.is_reddit:
            raise Exception('This test is for localhost only.')

    def test_create_existing_subreddit(self):
        self.r.login(self.un, '1111')
        self.assertRaises(errors.APIException, self.r.create_subreddit,
                          self.sr, 'foo')

    def test_create_redditor(self):
        unique_name = 'PyApiTestUser%d' % random.randint(3, 10240)
        self.r.create_redditor(unique_name, '1111')

    def test_create_subreddit(self):
        unique_name = 'test%d' % random.randint(3, 10240)
        description = '#Welcome to %s\n\n0 item 1\n0 item 2\n' % unique_name
        self.r.login(self.un, '1111')
        self.r.create_subreddit(unique_name, 'The %s' % unique_name,
                                description)

    def test_failed_feedback(self):
        self.assertRaises(errors.APIException, self.r.send_feedback,
                          'a', 'b', 'c')

    def test_send_feedback(self):
        msg = 'You guys are awesome. (Sent from the PRAW python module).'
        self.r.send_feedback('Bryce Boe', 'foo@foo.com', msg)


class MessageTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_deprecated_compose(self):
        subject = 'Deprecated Test'
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter('always')
            self.r.user.compose_message(subject, 'Message content')
            self.assertEqual(len(warning), 1)
            self.assertEqual(warning[0].category, DeprecationWarning)
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter('always')
            self.r.compose_message(self.r.user, subject, 'Message content')
            self.assertEqual(len(warning), 1)
            self.assertEqual(warning[0].category, DeprecationWarning)

    def test_mark_as_read(self):
        oth = Reddit(USER_AGENT)
        oth.login('PyApiTestUser3', '1111')
        # pylint: disable-msg=E1101
        msg = six_next(oth.user.get_unread(limit=1))
        msg.mark_as_read()
        self.assertTrue(msg not in oth.user.get_unread(limit=5))

    def test_mark_as_unread(self):
        oth = Reddit(USER_AGENT)
        oth.login('PyApiTestUser3', '1111')
        found = None
        for msg in oth.user.get_inbox():
            if not msg.new:
                found = msg
                msg.mark_as_unread()
                break
        else:
            self.fail('Could not find a read message.')
        self.assertTrue(found in oth.user.get_unread())

    def test_mark_multiple_as_read(self):
        oth = Reddit(USER_AGENT)
        oth.login('PyApiTestUser3', '1111')
        messages = []
        for msg in oth.user.get_unread(limit=None):
            if msg.author != oth.user.name:
                messages.append(msg)
                if len(messages) >= 2:
                    return
        self.assertEqual(2, len(messages))
        self.r.user.mark_as_read(messages)
        unread = oth.user.get_unread(limit=5)
        for msg in messages:
            self.assertTrue(msg not in unread)

    def test_modmail_send(self):
        subject = 'Unique message: %s' % uuid.uuid4()
        self.r.get_subreddit(self.sr).send_message(subject, 'Content')
        for msg in self.r.user.get_modmail():
            if msg.subject == subject:
                break
        else:
            self.fail('Could not find the message we just sent to ourself.')

    def test_reply_to_message_and_verify(self):
        text = 'Unique message reply: %s' % uuid.uuid4()
        found = None
        for msg in self.r.user.get_inbox():
            if isinstance(msg, Message) and msg.author == self.r.user:
                found = msg
                break
        else:
            self.fail('Could not find a self-message in the inbox')
        reply = found.reply(text)
        self.assertEqual(reply.parent_id, found.content_id)

    def test_send(self):
        subject = 'Unique message: %s' % uuid.uuid4()
        self.r.user.send_message(subject, 'Message content')
        for msg in self.r.user.get_inbox():
            if msg.subject == subject:
                break
        else:
            self.fail('Could not find the message we just sent to ourself.')


class ModeratorSubmissionTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_approve(self):
        submission = six_next(self.subreddit.get_spam())
        if not submission:
            self.fail('Could not find a submission to approve.')
        submission.approve()
        for approved in self.subreddit.get_new_by_date():
            if approved.id == submission.id:
                break
        else:
            self.fail('Could not find approved submission.')

    def test_remove(self):
        submission = six_next(self.subreddit.get_new_by_date())
        if not submission:
            self.fail('Could not find a submission to remove.')
        submission.remove()
        for removed in self.subreddit.get_spam():
            if removed.id == submission.id:
                break
        else:
            self.fail('Could not find removed submission.')


class ModeratorUserTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)
        self.other = self.r.get_redditor('pyapitestuser3', fetch=True)

    def test_ban(self):
        self.subreddit.ban(self.other)
        self.assertTrue(self.other in self.subreddit.get_banned())

    def test_make_contributor(self):
        self.subreddit.make_contributor(self.other)
        self.assertTrue(self.other in self.subreddit.get_contributors())

    def test_make_moderator(self):
        self.subreddit.make_moderator(self.other)
        self.assertTrue(self.other in self.subreddit.get_moderators())

    def test_make_moderator_by_name(self):
        self.subreddit.make_moderator(text_type(self.other))
        self.assertTrue(self.other in self.subreddit.get_moderators())

    def test_remove_contributor(self):
        self.subreddit.remove_contributor(self.other)
        self.assertFalse(self.other in self.subreddit.get_contributors())

    def test_remove_moderator(self):
        self.subreddit.remove_moderator(self.other)
        self.assertFalse(self.other in self.subreddit.get_moderators())

    def test_unban(self):
        self.subreddit.unban(self.other)
        self.assertFalse(self.other in self.subreddit.get_banned())


class RedditorTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.other_user = self.r.get_redditor(self.other_user_name)

    def test_friend(self):
        self.other_user.friend()

    def test_get_disliked(self):
        # Pulls from get_liked. Problem here may come from get_liked
        item = six_next(self.r.user.get_liked())
        item.downvote()
        self.delay()  # The queue needs to be processed
        self.assertFalse(item in list(self.r.user.get_liked()))

    def test_get_hidden(self):
        item = six_next(self.r.user.get_hidden())
        item.unhide()
        self.delay()  # The queue needs to be processed
        self.assertFalse(item in list(self.r.user.get_hidden()))

    def test_get_liked(self):
        # Pulls from get_disliked. Problem here may come from get_disliked
        item = six_next(self.r.user.get_disliked())
        item.upvote()
        self.delay()  # The queue needs to be processed
        self.assertFalse(item in list(self.r.user.get_disliked()))

    def test_get_redditor(self):
        self.assertEqual(self.other_user_id, self.other_user.id)

    def test_unfriend(self):
        self.other_user.unfriend()

    def test_user_set_on_login(self):
        self.assertTrue(isinstance(self.r.user, LoggedInRedditor))


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
            self.fail("Couldn't find a unhidden submission")
        found.hide()
        found.refresh()
        self.assertTrue(found.hidden)

    def test_report(self):
        # login as new user to report submission
        oth = Reddit(USER_AGENT)
        oth.login('PyApiTestUser3', '1111')
        subreddit = oth.get_subreddit(self.sr)
        submission = None
        for submission in subreddit.get_new_by_date():
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
        for item in self.r.get_saved_links():
            if item == submission:
                break
        else:
            self.fail('Could not find submission in saved links.')

    def test_short_link(self):
        submission = six_next(self.r.get_new(url_data={'sort': 'new'}))
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
        self.assertRaises(errors.APIException, self.r.submit, self.sr,
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


class SubredditTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_attribute_error(self):
        self.assertRaises(AttributeError, getattr, self.subreddit, 'foo')

    def test_get_modqueue(self):
        mod_submissions = list(self.r.get_subreddit('mod').get_modqueue())
        self.assertTrue(len(mod_submissions) > 0)

    def test_get_modqueue_multi(self):
        multi = '{0}+{1}'.format(self.sr, 'reddit_api_test2')
        mod_submissions = list(self.r.get_subreddit(multi).get_modqueue())
        self.assertTrue(len(mod_submissions) > 0)

    def test_moderator_required(self):
        oth = Reddit(USER_AGENT)
        oth.login('PyApiTestUser3', '1111')
        self.assertRaises(errors.ModeratorRequired, oth.get_settings, self.sr)

    def test_moderator_required_multi(self):
        sub = self.r.get_subreddit('{0}+{1}'.format(self.sr, 'test'))
        self.assertRaises(errors.ModeratorRequired, sub.get_modqueue)

    def test_my_contributions(self):
        for subreddit in self.r.user.my_contributions():
            if text_type(subreddit) == self.sr:
                break
        else:
            self.fail('Could not find contributed reddit in my_contributions.')

    def test_my_moderation(self):
        for subreddit in self.r.user.my_moderation():
            if text_type(subreddit) == self.sr:
                break
        else:
            self.fail('Could not find moderated reddit in my_moderation.')

    def test_my_reddits(self):
        for subreddit in self.r.user.my_reddits():
            # pylint: disable-msg=W0212
            self.assertTrue(text_type(subreddit) in subreddit._info_url)

    def test_nsfw_subreddit(self):
        self.disable_cache()
        originally_nsfw = self.subreddit.over18
        if originally_nsfw:
            self.subreddit.unmark_as_nsfw()
        else:
            self.subreddit.mark_as_nsfw()
        self.subreddit.refresh()
        self.assertNotEqual(originally_nsfw, self.subreddit.over18)
        if self.subreddit.over18:
            self.subreddit.unmark_as_nsfw()
        else:
            self.subreddit.mark_as_nsfw()
        self.subreddit.refresh()
        self.assertEqual(originally_nsfw, self.subreddit.over18)

    def test_search(self):
        if not self.r.config.is_reddit:
            raise Exception('Search does not work locally.')
        self.assertTrue(len(list(self.subreddit.search('test'))) > 0)

    def test_subscribe_and_verify(self):
        self.subreddit.subscribe()
        for subreddit in self.r.user.my_reddits():
            if text_type(subreddit) == self.sr:
                break
        else:
            self.fail('Could not find reddit in my_reddits.')

    def test_subscribe_by_name_and_verify(self):
        self.r.subscribe(self.sr)
        for subreddit in self.r.user.my_reddits():
            if text_type(subreddit) == self.sr:
                break
        else:
            self.fail('Could not find reddit in my_reddits.')

    def test_unsubscribe_and_verify(self):
        self.subreddit.unsubscribe()
        for subreddit in self.r.user.my_reddits():
            if text_type(subreddit) == self.sr:
                self.fail('Found reddit in my_reddits.')

    def test_unsubscribe_by_name_and_verify(self):
        self.r.unsubscribe(self.sr)
        for subreddit in self.r.user.my_reddits():
            if text_type(subreddit) == self.sr:
                self.fail('Found reddit in my_reddits.')


if __name__ == '__main__':
    unittest.main()
