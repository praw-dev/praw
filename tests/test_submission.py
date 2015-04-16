"""Tests for Subreddit class."""

from __future__ import print_function, unicode_literals
from praw import errors
from requests.exceptions import HTTPError
from .helper import PRAWTest, betamax


class SubmissionTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd)
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax
    def test_mark_as_nsfw__exception(self):
        found = next(self.r.get_subreddit('all').get_top())
        self.assertRaises(errors.ModeratorOrScopeRequired, found.mark_as_nsfw)

    @betamax
    def test_mark_as_nsfw_and_umark_as_nsfw__as_author(self):
        self.r.login(self.other_non_mod_name, self.other_non_mod_pswd)
        submission = self.r.get_submission(submission_id="1nt8co")
        self.assertEqual(self.r.user, submission.author)

        submission.mark_as_nsfw()
        self.assertTrue(submission.refresh().over_18)
        submission.unmark_as_nsfw()
        self.assertFalse(submission.refresh().over_18)

    @betamax
    def test_submit__duplicate_url(self):
        url = 'https://praw.readthedocs.org/'
        self.assertRaises(errors.AlreadySubmitted, self.subreddit.submit,
                          'PRAW Documentation', url=url)
        submission = self.subreddit.submit(
            'PRAW Documentation try 2', url=url, resubmit=True)
        self.assertEqual('PRAW Documentation try 2', submission.title)
        self.assertEqual(url, submission.url)

    @betamax
    def test_submission_edit__link_failure(self):
        predicate = lambda item: not item.is_self
        found = self.first(self.r.user.get_submitted(), predicate)
        self.assertRaises(HTTPError, found.edit, 'text')

    @betamax
    def test_submission_edit__self(self):
        predicate = lambda item: item.is_self
        found = self.first(self.r.user.get_submitted(), predicate)
        content = '' if len(found.selftext) > 100 else found.selftext + 'a'
        self.assertEqual(content, found.edit(content).selftext)

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
    def test_submit__self(self):
        submission = self.r.submit(self.sr, 'Title', text='BODY')
        self.assertEqual('Title', submission.title)
        self.assertEqual('BODY', submission.selftext)

    @betamax
    def test_submit__self_with_no_body(self):
        submission = self.r.submit(self.sr, 'Title', text='')
        self.assertEqual('Title', submission.title)
        self.assertEqual('', submission.selftext)

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
    def test_distinguish_and_undistinguish(self):
        submission_id = self.submission_edit_id
        submission = self.r.get_submission(submission_id=submission_id)

        submission.distinguish()
        self.assertTrue(submission.refresh().distinguished)
        submission.undistinguish()
        self.assertFalse(submission.refresh().distinguished)

    @betamax
    def test_mark_as_nsfw_and_umark_as_nsfw__as_moderator(self):
        submission = self.r.get_submission(submission_id="1nt8co")
        self.assertNotEqual(self.r.user, submission.author)

        submission.mark_as_nsfw()
        self.assertTrue(submission.refresh().over_18)
        submission.unmark_as_nsfw()
        self.assertFalse(submission.refresh().over_18)

    @betamax
    def test_sticky_unsticky(self):
        submission_id = self.submission_edit_id
        submission = self.r.get_submission(submission_id=submission_id)
        submission.sticky()
        self.assertTrue(submission.refresh().stickied)
        submission.unsticky()
        self.assertFalse(submission.refresh().stickied)
