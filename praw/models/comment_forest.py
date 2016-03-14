"""Provide CommentForest for Submission comments."""
from heapq import heappop, heappush

from .reddit.more import MoreComments


class CommentForest(object):
    """A forest of comments starts with  multiple top-level comments.

    Each of these comments can be a tree of replies.

    """

    @staticmethod
    def _extract_more_comments(tree):
        """Return a list of MoreComments objects removed from tree."""
        more_comments = []
        queue = [(None, x) for x in tree]
        while len(queue) > 0:
            parent, comm = queue.pop(0)
            if isinstance(comm, MoreComments):
                heappush(more_comments, comm)
                if parent:
                    parent.replies.remove(comm)
                else:
                    tree.remove(comm)
            else:
                for item in comm.replies:
                    queue.append((comm, item))
        return more_comments

    def __getitem__(self, index):
        """Return the comment at position ``index`` in the list."""
        return self._comments[index]

    def __init__(self, submission, comments):
        """Initialize a CommentForest instance.

        :param submission: An instance of :class:`~.Subreddit` that is the
            parent of the comments.
        :param comments: A list of raw comments.

        """
        self._comments = comments
        self._comments_by_id = {}
        self._orphaned = {}
        self._replaced_more = False
        self._submission = submission

    def __len__(self):
        """Return the number of top-level comments in the forest."""
        return len(self._comments)

    def _insert_comment(self, comment):
        if comment.name in self._comments_by_id:  # Skip existing comments
            return

        comment._update_submission(self)
        if comment.name in self._orphaned:  # Reunite children with parent
            comment.replies.extend(self._orphaned[comment.name])
            del self._orphaned[comment.name]

        if comment.is_root:
            self._comments.append(comment)
        elif comment.parent_id in self._comments_by_id:
            self._comments_by_id[comment.parent_id].replies.append(comment)
        else:  # Orphan
            if comment.parent_id in self._orphaned:
                self._orphaned[comment.parent_id].append(comment)
            else:
                self._orphaned[comment.parent_id] = [comment]

    def replace_more_comments(self, limit=32, threshold=1):
        """Update the comment tree by replacing instances of MoreComments.

        :param limit: The maximum number of MoreComments objects to
            replace. Each replacement requires 1 API request. Set to None to
            have no limit, or to 0 to make no extra requests. Default: 32
        :param threshold: The minimum number of children comments a
            MoreComments object must have in order to be replaced. Default: 1
        :returns: A list of MoreComments objects that were not replaced.

        Note that after making this call, the `comments` attribute of the
        submission will no longer contain any MoreComments objects. Items that
        weren't replaced are still removed from the tree, and will be included
        in the returned list.

        """
        if self._replaced_more:
            return []

        remaining = limit
        more_comments = self._extract_more_comments(self._comments)
        skipped = []

        # Fetch largest more_comments until reaching the limit or the threshold
        while more_comments:
            item = heappop(more_comments)
            if remaining == 0:  # We're not going to replace any more
                heappush(more_comments, item)  # It wasn't replaced
                break
            elif len(item.children) == 0 or 0 < item.count < threshold:
                heappush(skipped, item)  # It wasn't replaced
                continue

            # Fetch new comments and decrease remaining if a request was made
            new_comments = item.comments(update=False)
            if new_comments is not None and remaining is not None:
                remaining -= 1
            elif new_comments is None:
                continue

            # Re-add new MoreComment objects to the heap of more_comments
            for more in self._extract_more_comments(new_comments):
                more._update_submission(self)
                heappush(more_comments, more)
            # Insert the new comments into the tree
            for comment in new_comments:
                self._insert_comment(comment)

        self._replaced_more = True
        return more_comments + skipped
