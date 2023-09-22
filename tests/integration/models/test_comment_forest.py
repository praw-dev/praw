"""Test praw.models.comment_forest."""

import pytest

from praw.exceptions import DuplicateReplaceException
from praw.models import Comment, MoreComments, Submission

from .. import IntegrationTest


class TestCommentForest(IntegrationTest):
    @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
    def test_comment_forest_refresh_error(self, reddit):
        reddit.read_only = False
        submission = next(reddit.front.top())
        submission.comment_limit = 1
        submission.comments[1].comments()
        with pytest.raises(DuplicateReplaceException):
            submission.comments.replace_more(limit=1)

    @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
    def test_replace__all(self, reddit):
        submission = Submission(reddit, "3hahrw")
        before_count = len(submission.comments.list())
        skipped = submission.comments.replace_more(limit=None, threshold=0)
        assert len(skipped) == 0
        assert all(isinstance(x, Comment) for x in submission.comments.list())
        assert all(x.submission == submission for x in submission.comments.list())
        assert before_count < len(submission.comments.list())

    @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
    def test_replace__all_large(self, reddit):
        submission = Submission(reddit, "n49rw")
        skipped = submission.comments.replace_more(limit=None, threshold=0)
        assert len(skipped) == 0
        assert all(isinstance(x, Comment) for x in submission.comments.list())
        assert len(submission.comments.list()) > 1000
        assert len(submission.comments.list()) == len(submission._comments_by_id)

    @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
    def test_replace__all_with_comment_limit(self, reddit):
        submission = Submission(reddit, "3hahrw")
        submission.comment_limit = 10
        skipped = submission.comments.replace_more(limit=None, threshold=0)
        assert len(skipped) == 0
        assert len(submission.comments.list()) >= 500

    @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
    def test_replace__all_with_comment_sort(self, reddit):
        submission = Submission(reddit, "3hahrw")
        submission.comment_sort = "old"
        skipped = submission.comments.replace_more(limit=None, threshold=0)
        assert len(skipped) == 0
        assert len(submission.comments.list()) >= 500

    @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
    def test_replace__on_comment_from_submission(self, reddit):
        submission = Submission(reddit, "3hahrw")
        types = [type(x) for x in submission.comments.list()]
        assert types.count(Comment) == 472
        assert types.count(MoreComments) == 18
        assert submission.comments[0].replies.replace_more() == []
        types = [type(x) for x in submission.comments.list()]
        assert types.count(Comment) == 489
        assert types.count(MoreComments) == 11

    @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
    def test_replace__on_direct_comment(self, reddit):
        comment = reddit.comment("d8r4im1")
        comment.refresh()
        assert any(isinstance(x, MoreComments) for x in comment.replies.list())
        comment.replies.replace_more()
        assert all(isinstance(x, Comment) for x in comment.replies.list())

    @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
    def test_replace__skip_all(self, reddit):
        submission = Submission(reddit, "3hahrw")
        before_count = len(submission.comments.list())
        skipped = submission.comments.replace_more(limit=0)
        assert len(skipped) == 18
        assert all(x.submission == submission for x in skipped)
        after_count = len(submission.comments.list())
        assert before_count == after_count + len(skipped)

    @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
    def test_replace__skip_at_limit(self, reddit):
        submission = Submission(reddit, "3hahrw")
        skipped = submission.comments.replace_more(limit=1)
        assert len(skipped) == 17

    @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
    def test_replace__skip_below_threshold(self, reddit):
        submission = Submission(reddit, "3hahrw")
        before_count = len(submission.comments.list())
        skipped = submission.comments.replace_more(limit=16, threshold=5)
        assert len(skipped) == 13
        assert all(x.count < 5 for x in skipped)
        assert all(x.submission == submission for x in skipped)
        assert before_count < len(submission.comments.list())
