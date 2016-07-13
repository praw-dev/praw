from praw.models import Comment, Submission
import mock
import pytest

from ... import IntegrationTest


class TestSubmission(IntegrationTest):
    def test_comments(self):
        with self.recorder.use_cassette(
                'TestSubmission.test_comments'):
            submission = Submission(self.reddit, '2gmzqe')
            assert len(submission.comments) == 1
            assert isinstance(submission.comments[0], Comment)
            assert isinstance(submission.comments[0].replies[0], Comment)

    def test_clear_vote(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_clear_vote'):
            Submission(self.reddit, '4b536p').clear_vote()

    @mock.patch('time.sleep', return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_delete'):
            submission = Submission(self.reddit, '4b1tfm')
            submission.delete()
            assert submission.author is None
            assert submission.selftext == '[deleted]'

    def test_downvote(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_downvote'):
            Submission(self.reddit, '4b536p').downvote()

    @mock.patch('time.sleep', return_value=None)
    def test_edit(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_edit'):
            submission = Submission(self.reddit, '4b1tfm')
            submission.edit('New text')
            assert submission.selftext == 'New text'

    def test_duplicates(self):
        with self.recorder.use_cassette(
                'TestSubmission.test_duplicates'):
            submission = Submission(self.reddit, 'avj2v')
            assert len(list(submission.duplicates())) > 0

    def test_hide(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_hide'):
            Submission(self.reddit, '4b1tfm').hide()

    def test_invalid_attribute(self):
        with self.recorder.use_cassette(
                'TestSubmission.test_invalid_attribute'):
            submission = Submission(self.reddit, '2gmzqe')
            with pytest.raises(AttributeError) as excinfo:
                submission.invalid_attribute
        assert excinfo.value.args[0] == ("'Submission' object has no attribute"
                                         " 'invalid_attribute'")

    def test_reply(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_reply'):
            submission = Submission(self.reddit, '4b1tfm')
            comment = submission.reply('Test reply')
            assert comment.author == self.reddit.config.username
            assert comment.body == 'Test reply'
            assert comment.parent_id == submission.fullname

    def test_report(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_report'):
            Submission(self.reddit, '4b536h').report('praw')

    def test_save(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_save'):
            Submission(self.reddit, '4b536p').save()

    def test_unhide(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_unhide'):
            Submission(self.reddit, '4b1tfm').unhide()

    def test_unsave(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_unsave'):
            Submission(self.reddit, '4b536p').unsave()

    def test_upvote(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_upvote'):
            Submission(self.reddit, '4b536p').upvote()


class TestSubmissionModeration(IntegrationTest):
    def test_contest_mode(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_contest_mode'):
            submission = Submission(self.reddit, '4s2idz')
            submission.mod.contest_mode()

    def test_contest_mode__disable(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_contest_mode__disable'):
            submission = Submission(self.reddit, '4s2idz')
            submission.mod.contest_mode(state=False)

    def test_nsfw(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_nsfw'):
            Submission(self.reddit, '4s2idz').mod.nsfw()

    def test_sfw(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_sfw'):
            Submission(self.reddit, '4s2idz').mod.sfw()
