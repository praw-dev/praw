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

import unittest
from six import next as six_next

from helper import AuthenticatedHelper, first, USER_AGENT
from praw import errors, Reddit


class SubmissionTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_clear_vote(self):
        submission = first(self.r.user.get_submitted(),
                           lambda submission: submission.likes is False)
        self.assertTrue(submission is not None)
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
        submission = first(self.r.user.get_submitted(),
                           lambda submission: submission.likes is True)
        self.assertTrue(submission is not None)
        submission.downvote()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertEqual(submission.likes, False)

    def test_hide(self):
        self.disable_cache()
        found = first(self.r.user.get_submitted(),
                      lambda item: not item.hidden)
        self.assertTrue(found is not None)
        found.hide()
        found.refresh()
        self.assertTrue(found.hidden)

    def test_report(self):
        # login as new user to report submission
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login('PyAPITestUser3', '1111')
        subreddit = oth.get_subreddit(self.sr)
        submission = first(subreddit.get_new(),
                           lambda submission: not submission.hidden)
        self.assertTrue(submission is not None)
        submission.report()
        # check if submission was reported
        found_report = first(self.r.get_subreddit(self.sr).get_reports(),
                             lambda report: report.id == submission.id)
        self.assertTrue(found_report is not None)

    def test_save(self):
        submission = first(self.r.user.get_submitted(),
                           lambda submission: not submission.saved)
        self.assertTrue(submission is not None)
        submission.save()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertTrue(submission.saved)
        # verify in saved_links
        saved = first(self.r.user.get_saved(),
                      lambda item: item == submission)
        self.assertTrue(saved is not None)

    def test_short_link(self):
        submission = six_next(self.r.get_new())
        if self.r.config.is_reddit:
            self.assertTrue(submission.id in submission.short_link)
        else:
            self.assertRaises(errors.ClientException, getattr, submission,
                              'short_link')

    def test_unhide(self):
        self.disable_cache()
        found = first(self.r.user.get_submitted(),
                      lambda item: item.hidden)
        self.assertTrue(found is not None)
        found.unhide()
        found.refresh()
        self.assertFalse(found.hidden)

    def test_unsave(self):
        submission = first(self.r.user.get_submitted(),
                           lambda submission: submission.saved)
        self.assertTrue(submission is not None)
        submission.unsave()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertFalse(submission.saved)

    def test_upvote(self):
        submission = first(self.r.user.get_submitted(),
                           lambda submission: submission.likes is None)
        self.assertTrue(submission is not None)
        submission.upvote()
        # reload the submission
        submission = self.r.get_submission(submission_id=submission.id)
        self.assertEqual(submission.likes, True)
