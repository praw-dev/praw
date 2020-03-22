"""Container for SubredditHelper."""
from typing import Optional

from ..base import PRAWBase
from ..reddit.subreddit import Subreddit


class SubredditHelper(PRAWBase):
    """Provide a set of functions to interact with Subreddits."""

    def __call__(self, display_name: str) -> Subreddit:
        """Return a lazy instance of :class:`~.Subreddit`.

        :param display_name: The name of the subreddit.
        """
        lower_name = display_name.lower()

        if lower_name == "random":
            return self._reddit.random_subreddit()
        if lower_name == "randnsfw":
            return self._reddit.random_subreddit(nsfw=True)

        return Subreddit(self._reddit, display_name=display_name)

    def create(
        self,
        name: str,
        title: Optional[str] = None,
        link_type: str = "any",
        subreddit_type: str = "public",
        wikimode: str = "disabled",
        **other_settings: Optional[str]
    ) -> Subreddit:
        """Create a new subreddit.

        :param name: The name for the new subreddit.

        :param title: The title of the subreddit. When ``None`` or ``''`` use
            the value of ``name``.

        :param link_type: The types of submissions users can make.
            One of ``any``, ``link``, ``self`` (default: any).
        :param subreddit_type: One of ``archived``, ``employees_only``,
            ``gold_only``, ``gold_restricted``, ``private``, ``public``,
            ``restricted`` (default: public).
        :param wikimode: One of  ``anyone``, ``disabled``, ``modonly``.

        See :meth:`~.SubredditModeration.update` for documentation of other
        available settings.

        Any keyword parameters not provided, or set explicitly to None, will
        take on a default value assigned by the Reddit server.

        """
        Subreddit._create_or_update(
            _reddit=self._reddit,
            name=name,
            link_type=link_type,
            subreddit_type=subreddit_type,
            title=title or name,
            wikimode=wikimode,
            **other_settings
        )
        return self(name)
