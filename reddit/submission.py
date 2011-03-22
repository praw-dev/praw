from base_objects import RedditContentObject
from features import Saveable, Voteable, Deletable
from urls import urls
from util import urljoin

class Submission(RedditContentObject, Saveable, Voteable,  Deletable):
    """A class for submissions to Reddit."""

    kind = "t3"

    def __init__(self, reddit_session, title=None, json_dict=None,
                 fetch_comments=True):
        super(Submission, self).__init__(reddit_session, title, json_dict,
                                         fetch=True)
        if not self.permalink.startswith(urls["reddit_url"]):
            self.permalink = urljoin(urls["reddit_url"], self.permalink)

    def __str__(self):
        title = self.title.replace("\r\n", "")
        return "{0} :: {1}".format(self.score, title.encode("utf-8"))

    @property
    def comments(self):
        submission_info, comment_info = self.reddit_session._request_json(
                                                            self.permalink)
        comments = comment_info["data"]["children"]
        return comments

    def add_comment(self, text):
        """If logged in, comment on the submission using the specified text."""
        return self.reddit_session._add_comment(self.name,
                                                subreddit_name=self.subreddit,
                                                text=text)

