"""Tests for Subreddit class."""

from __future__ import print_function, unicode_literals
from .helper import PRAWTest, betamax


class SubmissionTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd)
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax
    def test_submission_delete(self):
        submission = next(self.r.user.get_submitted())
        self.assertEqual(self.r.user, submission.author)
        submission.delete()
        self.assertEqual(None, submission.refresh().author)

    @betamax
    def test_submission_hide_and_unhide(self):
        submission = next(self.r.user.get_submitted())
        submission.hide()
        self.assertTrue(submission.refresh().hidden)
        submission.unhide()
        self.assertFalse(submission.refresh().hidden)

    @betamax
    def test_report(self):
        submission = next(self.subreddit.get_new())
        submission.report()
        self.assertEqual(submission, next(self.subreddit.get_reports()))

    @betamax
    def test_short_link(self):
        submission = next(self.r.get_new())
        self.assertTrue(submission.id in submission.short_link)

    @betamax
    def test_voting(self):
        submission = next(self.r.user.get_submitted())
        submission.downvote()
        self.assertEqual(False, submission.refresh().likes)
        submission.upvote()
        self.assertTrue(submission.refresh().likes)
        submission.clear_vote()
        self.assertEqual(None, submission.refresh().likes)


class SubmissionModeratorTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd)
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax
    def test_sticky_unsticky(self):
        submission_id = self.submission_edit_id
        submission = self.r.get_submission(submission_id=submission_id)
        submission.sticky()
        self.assertTrue(submission.refresh().stickied)
        submission.unsticky()
        self.assertFalse(submission.refresh().stickied)
