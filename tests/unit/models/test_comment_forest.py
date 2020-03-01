from praw.models.comment_forest import CommentForest

from .. import UnitTest


class TestCommentForest(UnitTest):
    def test_equality(self):
        assert CommentForest(self.reddit.submission("id")) != 5
