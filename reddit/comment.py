from features import Voteable, Deletable
from base_objects import RedditContentObject
from util import limit_chars

class Comment(RedditContentObject, Voteable,  Deletable):
    """A class for comments."""

    kind = "t1"

    def __init__(self, reddit_session, json_dict):
        super(Comment, self).__init__(reddit_session, None, json_dict, True)
        if self.replies:
            self.replies = self.replies["data"]["children"]
        else:
            self.replies = []

    @limit_chars()
    def __str__(self):
        return getattr(self, "body",
                       "[[ need to fetch more comments... ]]").encode("utf8")

    @property
    def is_root(self):
        return not bool(getattr(self, "parent", False))

    def reply(self, text):
        """Reply to the comment with the specified text."""
        return self.reddit_session._add_comment(self.name,
                                                subreddit_name=self.subreddit,
                                                text=text)

