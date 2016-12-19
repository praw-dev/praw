"""Test praw.models.comment_forest."""
from praw.models import Comment, MoreComments, Submission

from .. import IntegrationTest


class TestCommentForest(IntegrationTest):
    def setup(self):
        super(TestCommentForest, self).setup()
        # Responses do not decode well on travis so manually renable gzip.
        self.reddit._core._requestor._http.headers['Accept-Encoding'] = 'gzip'

    def test_replace__all(self):
        with self.recorder.use_cassette(
                'TestCommentForest.test_replace__all',
                match_requests_on=['uri', 'method', 'body']):
            submission = Submission(self.reddit, '3hahrw')
            before_count = len(submission.comments.list())
            skipped = submission.comments.replace_more(None, threshold=0)
            assert len(skipped) == 0
            assert all(x.submission == submission for x in
                       submission.comments.list())
            assert before_count < len(submission.comments.list())

    def test_replace__all_large(self):
        with self.recorder.use_cassette(
                'TestCommentForest.test_replace__all_large',
                match_requests_on=['uri', 'method', 'body']):
            submission = Submission(self.reddit, 'n49rw')
            skipped = submission.comments.replace_more(None, threshold=0)
            assert len(skipped) == 0
            assert len(submission.comments.list()) > 1000
            assert len(submission.comments.list()) == \
                len(submission._comments_by_id)

    def test_replace__all_with_comment_limit(self):
        with self.recorder.use_cassette(
                'TestCommentForest.test_replace__all_with_comment_limit',
                match_requests_on=['uri', 'method', 'body']):
            submission = Submission(self.reddit, '3hahrw')
            submission.comment_limit = 10
            skipped = submission.comments.replace_more(None, threshold=0)
            assert len(skipped) == 0
            assert len(submission.comments.list()) >= 500

    def test_replace__skip_at_limit(self):
        with self.recorder.use_cassette(
                'TestCommentForest.test_replace__skip_at_limit',
                match_requests_on=['uri', 'method', 'body']):
            submission = Submission(self.reddit, '3hahrw')
            skipped = submission.comments.replace_more(1)
            assert len(skipped) == 17

    def test_replace__skip_below_threshold(self):
        with self.recorder.use_cassette(
                'TestCommentForest.test_replace__skip_below_threshold',
                match_requests_on=['uri', 'method', 'body']):
            submission = Submission(self.reddit, '3hahrw')
            before_count = len(submission.comments.list())
            skipped = submission.comments.replace_more(16, 5)
            assert len(skipped) == 13
            assert all(x.count < 5 for x in skipped)
            assert all(x.submission == submission for x in skipped)
            assert before_count < len(submission.comments.list())

    def test_replace__skip_all(self):
        with self.recorder.use_cassette(
                'TestCommentForest.test_replace__skip_all',
                match_requests_on=['uri', 'method', 'body']):
            submission = Submission(self.reddit, '3hahrw')
            before_count = len(submission.comments.list())
            skipped = submission.comments.replace_more(limit=0)
            assert len(skipped) == 18
            assert all(x.submission == submission for x in skipped)
            after_count = len(submission.comments.list())
            assert before_count == after_count + len(skipped)

    def test_replace__on_comment_from_submission(self):
        with self.recorder.use_cassette(
                'TestCommentForest.test_replace__on_comment_from_submission',
                match_requests_on=['uri', 'method', 'body']):
            submission = Submission(self.reddit, '3hahrw')
            types = [type(x) for x in submission.comments.list()]
            assert types.count(Comment) == 472
            assert types.count(MoreComments) == 18
            assert submission.comments[0].replies.replace_more() == []
            types = [type(x) for x in submission.comments.list()]
            assert types.count(Comment) == 489
            assert types.count(MoreComments) == 11

    def test_replace__on_direct_comment(self):
        with self.recorder.use_cassette(
                'TestCommentForest.test_replace__on_direct_comment',
                match_requests_on=['uri', 'method', 'body']):
            comment = self.reddit.comment('d8r4im1')
            comment.refresh()
            assert any(isinstance(x, MoreComments) for x in
                       comment.replies.list())
            comment.replies.replace_more()
            assert all(isinstance(x, Comment) for x in
                       comment.replies.list())
