#!/usr/bin/env python

# This file is part of reddit_api.
#
# reddit_api is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# reddit_api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with reddit_api.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable-msg=C0103, R0903, R0904, W0201

import random
import time
import unittest
import uuid
import warnings
from urlparse import urljoin
from urllib2 import HTTPError

from reddit import Reddit, errors, VERSION
from reddit.objects import Comment, LoggedInRedditor, Message, MoreComments

USER_AGENT = 'reddit_api test suite %s' % VERSION


def flair_diff(root, other):
    """Function for comparing two flairlists supporting optional arguments."""
    keys = [u'user', u'flair_text', u'flair_css_class']
    root_items = set(tuple(item[key] if key in item and item[key] else u'' for
                           key in keys) for item in root)
    other_items = set(tuple(item[key] if key in item and item[key] else u'' for
                            key in keys) for item in other)
    return list(root_items - other_items)


class BasicHelper(object):
    def configure(self):
        self.r = Reddit(USER_AGENT)
        self.sr = 'reddit_api_test'
        self.un = 'PyApiTestUser2'

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
        if self.r.config.is_reddit:
            self.self = self.url('/r/programming/comments/bn2wi/')
        else:
            self.self = self.url('/r/bboe/comments/2z/tasdest/')

    def test_comments_contains_no_noncomment_objects(self):
        if self.r.config.is_reddit:
            url = self.url('/r/programming/comments/bn2wi/')
        else:
            url = self.url('/r/reddit_test9/comments/1a/')
        comments = self.r.get_submission(url=url).comments
        self.assertFalse([item for item in comments if not
                          (isinstance(item, Comment) or
                           isinstance(item, MoreComments))])

    def test_get_all_comments(self):
        num = 50
        self.assertEqual(num, len(list(self.r.get_all_comments(limit=num))))

    def test_get_front_page(self):
        num = 50
        self.assertEqual(num, len(list(self.r.get_front_page(limit=num))))

    def test_info_by_known_url_returns_known_id_link_post(self):
        if self.r.config.is_reddit:
            url = 'http://imgur.com/Vr8ZZ'
            comm = self.url('/r/UCSantaBarbara/comments/m77nc/')
        else:
            url = 'http://google.com/?q=82.1753988563'
            comm = self.url('/r/reddit_test8/comments/2s/')
        found_links = self.r.info(url)
        tmp = self.r.get_submission(url=comm)
        self.assertTrue(tmp in found_links)

    def test_info_by_self_url_raises_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            self.r.info(self.self)
            self.assertEqual(len(w), 1)
            self.assertEqual(w[-1].category, UserWarning)
            self.assertTrue('self' in str(w[-1].message))

    def test_info_by_url_also_found_by_id(self):
        if self.r.config.is_reddit:
            url = 'http://imgur.com/Vr8ZZ'
        else:
            url = 'http://google.com/?q=82.1753988563'
        found_link = self.r.info(url).next()  # pylint: disable-msg=E1101
        found_by_id = self.r.info(thing_id=found_link.content_id)
        self.assertTrue(found_by_id)
        self.assertTrue(found_link in found_by_id)

    def test_not_logged_in_submit(self):
        self.assertRaises(errors.LoginRequired, self.r.submit,
                          self.sr, 'TITLE', text='BODY')

    def test_not_logged_in_when_initialized(self):
        self.assertEqual(self.r.user, None)

    def test_require_user_agent(self):
        self.assertRaises(TypeError, Reddit, user_agent=None)

    def test_search_reddit_names(self):
        self.assertTrue(len(self.r.search_reddit_names('reddit')) > 0)


class MoreCommentsTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        if self.r.config.is_reddit:
            url = self.url('/r/blog/comments/f8aqy/')
            self.submission = self.r.get_submission(url=url)
        else:
            url = self.url('/r/reddit_test9/comments/1a/')
            self.submission = self.r.get_submission(url=url)

    def test_all_comments(self):
        c_len = len(self.submission.comments)
        cf_len = len(self.submission.comments_flat)
        ac_len = len(self.submission.all_comments)
        acf_len = len(self.submission.all_comments_flat)

        # pylint: disable-msg=W0212
        self.assertEqual(len(self.submission._comments_by_id), acf_len)
        self.assertTrue(c_len <= ac_len < cf_len < acf_len)


class CommentTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_add_comment_and_verify(self):
        text = 'Unique comment: %s' % uuid.uuid4()
        # pylint: disable-msg=E1101
        submission = self.subreddit.get_new_by_date().next()
        # pylint: enable-msg=E1101
        self.assertTrue(submission.add_comment(text))
        # reload the submission
        time.sleep(1)
        submission = self.r.get_submission(url=submission.permalink)
        for comment in submission.comments:
            if comment.body == text:
                break
        else:
            self.fail('Could not find comment that was just posted.')

    def test_add_reply_and_verify(self):
        text = 'Unique reply: %s' % uuid.uuid4()
        found = None
        for submission in self.subreddit.get_new_by_date():
            if submission.num_comments > 0:
                found = submission
                break
        if not found:
            self.fail('Could not find a submission with comments.')
        comment = found.comments[0]
        self.assertTrue(comment.reply(text))
        # reload the submission (use id to bypass cache)
        time.sleep(1)
        submission = self.r.get_submission(submission_id=found.id)
        for comment in submission.comments[0].replies:
            if comment.body == text:
                break
        else:
            self.fail('Could not find the reply that was just posted.')


class FlairTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_add_flair_by_subreddit_name(self):
        self.r.set_flair(self.sr, self.r.user, 'flair')

    def test_add_flair_to_invalid_user(self):
        self.assertRaises(errors.APIException, self.subreddit.set_flair, 'b')

    def test_add_flair_by_name(self):
        self.subreddit.set_flair(self.r.user.name, 'Awesome Mod (Name)', 'css')

    def test_add_flair_by_user(self):
        self.subreddit.set_flair(self.r.user, 'Awesome Mod (User)', 'css')

    def test_clear_user_flair(self):
        self.subreddit.set_flair(self.r.user)

    def test_flair_csv_and_flair_list(self):
        # Clear all flair
        self.subreddit.clear_all_flair()
        self.assertEqual([], list(self.subreddit.flair_list()))

        # Set flair
        flair_mapping = [{u'user':'bboe', u'flair_text':u'dev'},
                         {u'user':u'PyAPITestUser2', u'flair_css_class':u'xx'},
                         {u'user':u'PyAPITestUser3', u'flair_text':u'AWESOME',
                          u'flair_css_class':u'css'}]
        self.subreddit.set_flair_csv(flair_mapping)
        self.assertEqual([], flair_diff(flair_mapping,
                                        list(self.subreddit.flair_list())))

    def test_flair_csv_optional_args(self):
        flair_mapping = [{'user': 'bboe', 'flair_text': 'bboe'},
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

    def test_add_template(self):
        self.subreddit.add_flair_template('text', 'css', True)

    def test_clear(self):
        self.subreddit.clear_flair_templates()


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
        msg = 'You guys are awesome. (Sent from reddit_api python module).'
        self.r.send_feedback('Bryce Boe', 'foo@foo.com', msg)


class MessageTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_compose(self):
        subject = 'Unique message: %s' % uuid.uuid4()
        self.r.user.compose_message(subject, 'Message content')
        for msg in self.r.user.get_inbox():
            if msg.subject == subject:
                break
        else:
            self.fail('Could not find the message we just sent to ourself.')

    def test_mark_as_read(self):
        oth = Reddit(USER_AGENT)
        oth.login('PyApiTestUser3', '1111')
        msg = oth.user.get_unread(limit=1).next()  # pylint: disable-msg=E1101
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
        messages = list(oth.user.get_unread(limit=2))
        self.assertEqual(2, len(messages))
        self.r.user.mark_as_read(messages)
        unread = oth.user.get_unread(limit=5)
        for msg in messages:
            self.assertTrue(msg not in unread)

    def test_modmail(self):
        self.assertTrue(len(list(self.r.user.get_modmail())) > 0)

    def test_reply_to_message_and_verify(self):
        text = 'Unique message reply: %s' % uuid.uuid4()
        found = None
        for msg in self.r.user.get_inbox():
            if isinstance(msg, Message) and msg.author == self.r.user:
                found = msg
                break
        if not found:
            self.fail('Could not find a self-message in the inbox')
        found.reply(text)
        for msg in self.r.user.get_sent():
            if msg.body == text:
                break
        else:
            self.fail('Could not find the recently sent reply.')


class ModeratorTest(unittest.TestCase, AuthenticatedHelper):
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
        self.subreddit.make_moderator(str(self.other))
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
        if self.r.config.is_reddit:
            self.other = {'id': '6c1xj', 'name': 'PyApiTestUser3'}
        else:
            self.other = {'id': 'pa', 'name': 'PyApiTestUser3'}
        self.other_user = self.r.get_redditor(self.other['name'])

    def test_get_redditor(self):
        self.assertEqual(self.other['id'], self.other_user.id)

    def test_friend(self):
        self.other_user.friend()

    def test_unfriend(self):
        self.other_user.unfriend()

    def test_user_set_on_login(self):
        self.assertTrue(isinstance(self.r.user, LoggedInRedditor))

    def test_logout(self):
        tmp = self.r.modhash, self.r.user
        self.r.logout()
        self.r.modhash, self.r.user = tmp
        try:
            passed = False
            self.r.clear_flair_templates(self.sr)
        except HTTPError, e:
            if e.code == 403:
                passed = True
        if not passed:
            self.fail('Logout failed.')


class SubmissionTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_delete(self):
        submission = list(self.r.user.get_submitted())[-1]
        submission.delete()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertEqual('[deleted]', submission.author)

    def test_save(self):
        submission = None
        for submission in self.r.user.get_submitted():
            if not submission.saved:
                break
        if not submission or submission.saved:
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

    def test_unsave(self):
        submission = None
        for submission in self.r.user.get_submitted():
            if submission.saved:
                break
        if not submission or not submission.saved:
            self.fail('Could not find saved submission.')
        submission.unsave()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertFalse(submission.saved)

    def test_clear_vote(self):
        submission = None
        for submission in self.r.user.get_submitted():
            if submission.likes is False:
                break
        if not submission or submission.likes is not False:
            self.fail('Could not find a down-voted submission.')
        submission.clear_vote()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertEqual(submission.likes, None)

    def test_downvote(self):
        submission = None
        for submission in self.r.user.get_submitted():
            if submission.likes is True:
                break
        if not submission or submission.likes is not True:
            self.fail('Could not find an up-voted submission.')
        submission.downvote()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertEqual(submission.likes, False)

    def test_upvote(self):
        submission = None
        for submission in self.r.user.get_submitted():
            if submission.likes is None:
                break
        if not submission or submission.likes is not None:
            self.fail('Could not find a non-voted submission.')
        submission.upvote()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertEqual(submission.likes, True)

    def test_report(self):
        # login as new user to report submission
        oth = Reddit(USER_AGENT)
        oth.login('PyApiTestUser3', '1111')
        subreddit = oth.get_subreddit(self.sr)
        submission = None
        for submission in subreddit.get_new_by_date():
            if not submission.hidden:
                break
        if not submission or submission.hidden:
            self.fail('Could not find a non-reported submission.')
        submission.report()
        # check if submission was reported
        for report in self.r.get_subreddit(self.sr).get_reports():
            if report.id == submission.id:
                break
        else:
            self.fail('Could not find reported submission.')

    def test_remove(self):
        submission = self.sr.get_new_by_date()[0]
        if not submission:
            self.fail('Could not find a submission to remove.')
        submission.remove()
        # check if submission was removed
        for removed in self.sr.get_spam():
            if removed.id == submission.id:
                break
        else:
            self.fail('Could not find removed submission.')

    def test_approve(self):
        submission = self.sr.get_spam()[0]
        if not submission:
            self.fail('Could not find a submission to approve.')
        submission.approve()
        # check if submission was approved
        for approved in self.sr.get_new_by_date():
            if approved.id == submission.id:
                break
        else:
            self.fail('Could not find approved submission.')


class SubmissionCreateTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_create_duplicate(self):
        found = None
        for item in self.r.user.get_submitted():
            if not item.is_self:
                found = item
                break
        if not found:
            self.fail('Could not find link post')
        self.assertRaises(errors.APIException, self.r.submit, self.sr,
                          found.title, url=found.url)

    def test_create_link_through_subreddit(self):
        unique = uuid.uuid4()
        title = 'Test Link: %s' % unique
        url = 'http://bryceboe.com/?bleh=%s' % unique
        subreddit = self.r.get_subreddit(self.sr)
        self.assertTrue(subreddit.submit(title, url=url))

    def test_create_self_and_verify(self):
        title = 'Test Self: %s' % uuid.uuid4()
        self.assertTrue(self.r.submit(self.sr, title, text='BODY'))
        time.sleep(1)
        for item in self.r.user.get_submitted():
            if title == item.title:
                break
        else:
            self.fail('Could not find submission.')


class SubredditTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_attribute_error(self):
        self.assertRaises(AttributeError, getattr, self.subreddit, 'foo')

    def test_get_my_moderation(self):
        for subreddit in self.r.user.my_moderation():
            if subreddit.display_name == self.sr:
                break
        else:
            self.fail('Could not find moderated reddit in my_moderation.')

    def test_subscribe_and_verify(self):
        self.subreddit.subscribe()
        for subreddit in self.r.user.my_reddits():
            if subreddit.display_name == self.sr:
                break
        else:
            self.fail('Could not find reddit in my_reddits.')

    def test_unsubscribe_and_verify(self):
        self.subreddit.unsubscribe()
        for subreddit in self.r.user.my_reddits():
            if subreddit.display_name == self.sr:
                self.fail('Found reddit in my_reddits.')


if __name__ == '__main__':
    unittest.main()
