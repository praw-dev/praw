from ..redditmodel import RedditModel


class Messageable(RedditModel):
    """Interface for RedditContentObjects that can be messaged."""

    _methods = (('send_message', 'PMMix'),)
