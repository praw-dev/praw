"""Provide the MoreComments class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from praw.const import API_PATH
from praw.models.base import PRAWBase

if TYPE_CHECKING:
    import praw
    from praw import models
    from praw.models.comment_forest import CommentForest
    from praw.models.reddit.submission import Submission


class MoreComments(PRAWBase):
    """A class indicating there are more comments."""

    MAX_COMMENTS_IN_REPR = 4

    _comments: CommentForest | list[models.Comment | MoreComments] | None
    # Attached by CommentForest._gather_more_comments.
    _remove_from: list[models.Comment | MoreComments]
    children: list[str]
    count: int
    name: str
    parent_id: str
    submission: Submission

    def __eq__(self, other: object) -> bool:
        """Return ``True`` if these :class:`.MoreComments` instances are the same."""
        if isinstance(other, self.__class__):
            return self.count == other.count and self.children == other.children
        return super().__eq__(other)

    def __hash__(self) -> int:
        """Return the hash of the current instance."""
        return hash(self.__class__.__name__) ^ hash(str(self))

    def __init__(self, reddit: praw.Reddit, _data: dict[str, Any]) -> None:
        """Initialize a :class:`.MoreComments` instance."""
        # count, parent_id, and children are populated from _data by super().__init__;
        # submission is attached afterward by CommentForest. All are declared as class
        # attributes above, so they need no placeholder initialization here.
        super().__init__(reddit, _data=_data)
        self._comments = None

    def __lt__(self, other: MoreComments) -> bool:
        """Provide a sort order on the :class:`.MoreComments` object."""
        # To work with heapq a "smaller" item is the one with the most comments. We are
        # intentionally making the biggest element the smallest element to turn the
        # min-heap implementation in heapq into a max-heap.
        return self.count > other.count

    def __repr__(self) -> str:
        """Return an object initialization representation of the instance."""
        children = self.children[: self.MAX_COMMENTS_IN_REPR]
        if len(self.children) > self.MAX_COMMENTS_IN_REPR:
            children[-1] = "..."
        return f"<{self.__class__.__name__} count={self.count}, children={children!r}>"

    def _continue_comments(self, *, update: bool) -> CommentForest | list[models.Comment | MoreComments]:
        assert not self.children, "Please file a bug report with PRAW."
        parent = self._load_comment(self.parent_id.split("_", 1)[1])
        self._comments = parent.replies
        if update:
            for comment in self._comments:
                comment.submission = self.submission
        return self._comments

    def _load_comment(self, comment_id: str) -> models.Comment:
        path = f"{API_PATH['submission'].format(id=self.submission.id)}_/{comment_id}"
        _, comments = self._reddit.get(
            path,
            params={
                "limit": self.submission.comment_limit,
                "sort": self.submission.comment_sort,
            },
        )
        assert len(comments.children) == 1, "Please file a bug report with PRAW."
        return comments.children[0]

    def comments(self, *, update: bool = True) -> CommentForest | list[models.Comment | MoreComments]:
        """Fetch and return the comments for a single :class:`.MoreComments` object."""
        if self._comments is None:
            if self.count == 0:  # Handle "continue this thread"
                return self._continue_comments(update=update)
            assert self.children, "Please file a bug report with PRAW."
            data = {
                "children": ",".join(self.children),
                "link_id": self.submission.fullname,
                "sort": self.submission.comment_sort,
            }
            comments: list[models.Comment | MoreComments] = self._reddit.post(API_PATH["morechildren"], data=data)
            self._comments = comments
            if update:
                for comment in comments:
                    comment.submission = self.submission
        return self._comments
