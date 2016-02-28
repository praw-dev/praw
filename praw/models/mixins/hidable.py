from ..redditmodel import RedditModel


class Hidable(RedditModel):
    """Interface for objects that can be hidden."""

    def hide(self, _unhide=False):
        """Hide object in the context of the logged in user.

        :param _unhide: If True, unhide the item instead.  Use
            :meth:`~praw.objects.Hideable.unhide` instead of setting this
            manually.

        :returns: The json response from the server.

        """
        return self.reddit_session.hide(self.fullname, _unhide=_unhide)

    def unhide(self):
        """Unhide object in the context of the logged in user.

        :returns: The json response from the server.

        """
        return self.hide(_unhide=True)
