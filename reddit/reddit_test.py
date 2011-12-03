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

import itertools
import unittest
import util
import uuid
import warnings
from reddit import Reddit, errors
from reddit.comment import Comment, MoreComments
from reddit.redditor import LoggedInRedditor


class BasicHelper(object):
    def configure(self):
        self.r = Reddit('reddit_api test suite')
        self.sr = 'reddit_api_test'
        self.un = 'PyApiTestUser2'


class AuthenticatedHelper(BasicHelper):
    def configure(self):
        super(AuthenticatedHelper, self).configure()
        self.r.login(self.un, '1111')


class BasicTest(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()
        self.self = 'http://www.reddit.com/r/programming/comments/bn2wi/'

    def test_require_user_agent(self):
        self.assertRaises(TypeError, Reddit, user_agent=None)

    def test_not_logged_in_when_initialized(self):
        self.assertEqual(self.r.user, None)

    def test_not_logged_in_submit(self):
        self.assertRaises(errors.LoginRequired, self.r.submit,
                          self.sr, 'TITLE', text='BODY')

    def test_info_by_known_url_returns_known_id_link_post(self):
        url = 'http://imgur.com/Vr8ZZ'
        comm = 'http://www.reddit.com/r/UCSantaBarbara/comments/m77nc/'
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
        url = 'http://imgur.com/Vr8ZZ'
        comm = 'http://www.reddit.com/r/UCSantaBarbara/comments/m77nc/'
        found_links = self.r.info(url)
        for link in found_links:
            found_by_id = self.r.info(id=link.name)
            self.assertTrue(found_by_id)
            self.assertTrue(link in found_by_id)

    def test_comments_contains_no_noncomment_objects(self):
        url = 'http://www.reddit.com/r/programming/comments/bn2wi/'
        comments = self.r.get_submission(url=url).comments
        self.assertFalse([item for item in comments if not
                          (isinstance(item, Comment) or
                           isinstance(item, MoreComments))])


class CommentTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_add_comment_and_verify(self):
        text = 'Unique comment: %s' % uuid.uuid4()
        submission = self.subreddit.get_new_by_date().next()
        self.assertTrue(submission.add_comment(text))
        # reload the submission
        submission = self.r.get_submission(url=submission.permalink)
        for comment in submission.comments:
            if comment.body == text:
                break
        else:
            self.fail('Could not find comment that was just posted.')

    def test_add_reply_and_verify(self):
        text = 'Unique reply: %s' % uuid.uuid4()
        for submission in self.subreddit.get_new_by_date():
            if submission.num_comments > 0:
                comment = submission.comments[0]
                break
        else:
            self.fail('Could not find a submission with comments.')
        self.assertTrue(comment.reply(text))
        # reload the submission (use id to bypass cache)
        submission = self.r.get_submission(id=submission.id)
        for comment in submission.comments[0].replies:
            if comment.body == text:
                break
        else:
            self.fail('Could not find the reply that was just posted.')


class MessageTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_get_inbox(self):
        self.r.user.get_inbox()

    def test_get_sent(self):
        self.r.user.get_sent()

    def test_get_modmail(self):
        self.r.user.get_modmail()


class ModTest(unittest.TestCase, AuthenticatedHelper):
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

    def test_clear_flair(self):
        self.subreddit.set_flair(self.r.user)

    def test_flair_list(self):
        self.subreddit.set_flair(self.un, 'flair')
        self.assertTrue(self.subreddit.flair_list().next())

    def test_flair_csv(self):
        flair_mapping = [{'user': 'bboe', 'flair_text': 'dev',
                          'flair_css_class': ''},
                         {'user': 'pyapitestuser3', 'flair_text': '',
                          'flair_css_class': 'css2'},
                         {'user': 'pyapitestuser2', 'flair_text': 'AWESOME',
                          'flair_css_class': 'css'}]
        self.subreddit.set_flair_csv(flair_mapping)
        expected = set([tuple(x) for x in flair_mapping])
        result = set([tuple(x) for x in self.subreddit.flair_list()])
        self.assertTrue(not expected - result)

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


class RedditorTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.other = {'id': '6c1xj', 'name': 'PyApiTestUser3'}
        self.user = self.r.get_redditor(self.other['name'])

    def test_get(self):
        self.assertEqual(self.other['id'], self.user.id)

    def test_compose(self):
        self.user.compose_message('Message topic', 'Message content')

    def test_friend(self):
        self.user.friend()

    def test_unfriend(self):
        self.user.unfriend()

    def test_user_set_on_login(self):
        self.assertTrue(isinstance(self.r.user, LoggedInRedditor))


class SubmissionTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_delete(self):
        submission = list(self.r.user.get_submitted())[-1]
        submission.delete()
        # reload the submission
        submission = self.r.get_submission(id=submission.id)
        self.assertEqual('[deleted]', submission.author)

    def test_save(self):
        for submission in self.r.user.get_submitted():
            if not submission.saved:
                break
        else:
            self.fail('Could not find unsaved submission.')
        submission.save()
        # reload the submission
        submission = self.r.get_submission(id=submission.id)
        self.assertTrue(submission.saved)

    def test_unsave(self):
        for submission in self.r.user.get_submitted():
            if submission.saved:
                break
        else:
            self.fail('Could not find saved submission.')
        submission.unsave()
        # reload the submission
        submission = self.r.get_submission(id=submission.id)
        self.assertFalse(submission.saved)

    def test_clear_vote(self):
        for submission in self.r.user.get_submitted():
            if submission.likes == False:
                break
        else:
            self.fail('Could not find a down-voted submission.')
        submission.clear_vote()
        print submission, 'clear'
        # reload the submission
        submission = self.r.get_submission(id=submission.id)
        self.assertEqual(submission.likes, None)

    def test_downvote(self):
        for submission in self.r.user.get_submitted():
            if submission.likes == True:
                break
        else:
            self.fail('Could not find an up-voted submission.')
        submission.downvote()
        print submission, 'down'
        # reload the submission
        submission = self.r.get_submission(id=submission.id)
        self.assertEqual(submission.likes, False)

    def test_upvote(self):
        for submission in self.r.user.get_submitted():
            if submission.likes == None:
                break
        else:
            self.fail('Could not find a non-voted submission.')
        submission.upvote()
        print submission, 'up'
        # reload the submission
        submission = self.r.get_submission(id=submission.id)
        self.assertEqual(submission.likes, True)


class SubmissionCreateTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_create_link_and_duplicate(self):
        unique = uuid.uuid4()
        title = 'Test Link: %s' % unique
        url = 'http://bryceboe.com/?bleh=%s' % unique
        self.assertTrue(self.r.submit(self.sr, title, url=url))
        self.assertRaises(errors.APIException, self.r.submit, self.sr,
                          title, url=url)

    def test_create_self_and_verify(self):
        title = 'Test Self: %s' % uuid.uuid4()
        self.assertTrue(self.r.submit(self.sr, title, text='BODY'))
        for item in self.r.user.get_submitted():
            if title == item.title:
                break
        else:
            self.fail('Could not find submission.')


class SubredditTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    # TODO: Need to verify the subscription
    def test_subscribe(self):
        self.subreddit.subscribe()

    def test_unsubscribe(self):
        self.subreddit.unsubscribe()


if __name__ == '__main__':
    unittest.main()
