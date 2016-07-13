"""Tests for Submission class."""

from praw import errors
from praw.objects import Submission
from six import text_type
from .helper import OAuthPRAWTest, PRAWTest, betamax


class SubmissionTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax()
    def test_report(self):
        submission = next(self.subreddit.get_new())
        submission.report()
        self.assertEqual(submission, next(self.subreddit.get_reports()))

    @betamax()
    def test_save_submission(self):
        submission = next(self.r.user.get_submitted())

        submission.save()
        submission.refresh()
        self.assertTrue(submission.saved)
        self.first(self.r.user.get_saved(), lambda x: x == submission)

        submission.unsave()
        submission.refresh()
        self.assertFalse(submission.saved)
        self.assertFalse(submission in self.r.user.get_saved(params={'u': 1}))

    @betamax()
    def test_short_link(self):
        submission = next(self.r.get_new())
        self.assertTrue(submission.id in submission.short_link)

    @betamax()
    def test_submission_delete(self):
        submission = next(self.r.user.get_submitted())
        self.assertEqual(self.r.user, submission.author)
        submission.delete()
        self.assertEqual(None, submission.refresh().author)

    @betamax()
    def test_submission_edit__link_failure(self):
        found = self.first(self.r.user.get_submitted(),
                           lambda item: not item.is_self)
        self.assertRaises(errors.HTTPException, found.edit, 'text')

    @betamax()
    def test_submission_edit__self(self):
        found = self.first(self.r.user.get_submitted(),
                           lambda item: item.is_self)
        content = '' if len(found.selftext) > 100 else found.selftext + 'a'
        self.assertEqual(content, found.edit(content).selftext)

    @betamax()
    def test_submission_hide_and_unhide(self):
        submission = next(self.r.user.get_submitted())
        submission.hide()
        self.assertTrue(submission.refresh().hidden)
        submission.unhide()
        self.assertFalse(submission.refresh().hidden)

    @betamax()
    def test_submission_refresh(self):
        subreddit = self.r.get_subreddit(self.sr)
        submission = next(subreddit.get_top())
        same_submission = self.r.get_submission(submission_id=submission.id)
        submission.clear_vote() if submission.likes else submission.upvote()
        self.assertEqual(submission.likes, same_submission.likes)
        submission.refresh()
        self.assertNotEqual(submission.likes, same_submission.likes)

    @betamax()
    def test_submit__duplicate_url(self):
        url = 'https://praw.readthedocs.org/'
        self.assertRaises(errors.AlreadySubmitted, self.subreddit.submit,
                          'PRAW Documentation', url=url)
        submission = self.subreddit.submit(
            'PRAW Documentation try 2', url=url, resubmit=True)
        self.assertEqual('PRAW Documentation try 2', submission.title)
        self.assertEqual(url, submission.url)

    @betamax()
    def test_submit__invalid_arguments(self):
        for text, url in [(None, None), ('text', 'url'), ('', 'url')]:
            self.assertRaises(TypeError, self.subreddit.submit, 'Title',
                              text=text, url=url)

    @betamax()
    def test_submit__self(self):
        submission = self.r.submit(self.sr, 'Title', text='BODY')
        self.assertEqual('Title', submission.title)
        self.assertEqual('BODY', submission.selftext)

    @betamax()
    def test_submit__self_with_no_body(self):
        submission = self.r.submit(self.sr, 'Title', text='')
        self.assertEqual('Title', submission.title)
        self.assertEqual('', submission.selftext)

    @betamax()
    def test_unicode_submission(self):
        title = 'Wiki Entry on \xC3\x9C'
        url = 'http://en.wikipedia.org/\xC3\x9C?id={0}'.format(self.r.modhash)
        submission = self.subreddit.submit(title, url=url)
        self.assertTrue(title in text_type(submission))
        self.assertEqual(title, submission.title)
        self.assertEqual(url, submission.url)

    @betamax()
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
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax()
    def test_approve_and_remove(self):
        submission = next(self.subreddit.get_spam())
        self.assertEqual(None, submission.approved_by)
        self.assertTrue(submission.banned_by)

        submission.approve()
        submission.refresh()
        self.assertEqual(self.un, submission.approved_by.name)
        self.assertEqual(None, submission.banned_by)

        submission.remove()
        submission.refresh()
        self.assertEqual(None, submission.approved_by)
        self.assertEqual(self.un, submission.banned_by.name)

    @betamax()
    def test_distinguish_and_undistinguish(self):
        submission_id = self.submission_edit_id
        submission = self.r.get_submission(submission_id=submission_id)

        submission.distinguish()
        self.assertTrue(submission.refresh().distinguished)
        submission.undistinguish()
        self.assertFalse(submission.refresh().distinguished)

    @betamax()
    def test_ignore_and_unignore_reports(self):
        submission = next(self.subreddit.get_new())
        submission.ignore_reports()
        log = next(self.subreddit.get_mod_log())
        self.assertEqual('ignorereports', log.action)
        self.assertEqual(submission.fullname, log.target_fullname)

        submission.unignore_reports()
        log = next(self.subreddit.get_mod_log(params={'uniq': 2}))
        self.assertEqual('unignorereports', log.action)
        self.assertEqual(submission.fullname, log.target_fullname)

    @betamax()
    def test_set_suggested_sort(self):
        submission_id = self.submission_edit_id
        submission = self.r.get_submission(submission_id=submission_id)
        submission.set_suggested_sort('new')
        self.assertEqual(submission.refresh().suggested_sort, 'new')
        submission.set_suggested_sort('blank')
        self.assertEqual(submission.refresh().suggested_sort, None)

    @betamax()
    def test_equality_and_hash(self):
        subreddit = self.r.get_subreddit(self.sr)
        hot = list(subreddit.get_hot())

        submission = hot[0]
        same_submission = self.r.get_submission(submission_id=submission.id)
        another_submission = hot[1]

        self.assertNotEqual(id(submission), id(same_submission))
        self.assertEqual(submission.id, same_submission.id)
        self.assertEqual(hash(submission), hash(same_submission))
        self.assertEqual(submission, same_submission)

        self.assertNotEqual(submission.id, another_submission.id)
        self.assertNotEqual(hash(submission), hash(another_submission))
        self.assertNotEqual(submission, another_submission)


class OAuthSubmissionTest(OAuthPRAWTest):
    @betamax()
    def test_edit_oauth(self):
        self.r.refresh_access_information(self.refresh_token['edit'])
        submission = Submission.from_id(self.r, self.submission_edit_id)
        self.assertEqual(submission, submission.edit('Edited text'))

    @betamax()
    def test_get_priv_submission_comments_oauth(self):
        self.r.refresh_access_information(self.refresh_token['read'])
        submission = Submission.from_id(self.r, self.priv_submission_id)
        self.assertTrue(submission.comments)

    @betamax()
    def test_get_submission_by_url_oauth(self):
        url = ("https://www.reddit.com/r/reddit_api_test_priv/comments/16kbb7/"
               "google/")
        self.r.refresh_access_information(self.refresh_token['read'])
        submission = Submission.from_url(self.r, url)
        self.assertTrue(submission.num_comments != 0)

    @betamax()
    def test_hide_oauth(self):
        # Without the "read" scope, submission.hidden is always False.
        self.r.refresh_access_information(self.refresh_token['read+report'])
        submission = self.r.get_submission(
            submission_id=self.submission_hide_id)

        self.assertFalse(submission.hidden)
        submission.hide()
        self.assertTrue(submission.refresh().hidden)
        submission.unhide()
        self.assertFalse(submission.refresh().hidden)

    @betamax()
    def test_raise_invalidsubmission_oauth(self):
        self.r.refresh_access_information(self.refresh_token['submit'])
        submission = self.r.get_submission(
            submission_id=self.submission_deleted_id)
        self.assertRaises(errors.InvalidSubmission, submission.add_comment,
                          'test')
        invalid_post = errors.InvalidSubmission()
        self.assertEqual(invalid_post.ERROR_TYPE, str(invalid_post))

    @betamax()
    def test_remove_oauth(self):
        self.r.refresh_access_information(self.refresh_token['modposts'])
        Submission.from_id(self.r, self.submission_edit_id).remove()

    @betamax()
    def test_submit_oauth(self):
        self.r.refresh_access_information(self.refresh_token['submit'])
        result = self.r.submit(self.sr, 'OAuth Submit', text='Foo')
        self.assertTrue(isinstance(result, Submission))

    @betamax()
    def test_vote_oauth(self):
        self.r.refresh_access_information(self.refresh_token['vote'])
        submission = Submission.from_id(self.r, self.submission_edit_id)
        submission.clear_vote()
