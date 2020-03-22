"""Provide the SubredditRedditorFlairTemplates class."""

from .....const import API_PATH
from .templates import SubredditFlairTemplates


class SubredditRedditorFlairTemplates(SubredditFlairTemplates):
    """Provide functions to interact with Redditor flair templates."""

    def __iter__(self):
        """Iterate through the user flair templates.

        For example:

        .. code-block:: python

           for template in reddit.subreddit('NAME').flair.templates:
               print(template)


        """
        url = API_PATH["user_flair"].format(subreddit=self.subreddit)
        params = {"unique": self.subreddit._reddit._next_unique}
        for template in self.subreddit._reddit.get(url, params=params):
            yield template

    def add(
        self,
        text,
        css_class="",
        text_editable=False,
        background_color=None,
        text_color=None,
        mod_only=None,
        allowable_content=None,
        max_emojis=None,
    ):
        """Add a Redditor flair template to the associated subreddit.

        :param text: The flair template's text (required).
        :param css_class: The flair template's css_class (default: '').
        :param text_editable: (boolean) Indicate if the flair text can be
            modified for each Redditor that sets it (default: False).
        :param background_color: The flair template's new background color,
            as a hex color.
        :param text_color: The flair template's new text color, either
            ``'light'`` or ``'dark'``.
        :param mod_only: (boolean) Indicate if the flair can only be used by
            moderators.
        :param allowable_content: If specified, most be one of ``'all'``,
            ``'emoji'``, or ``'text'`` to restrict content to that type.
            If set to ``'emoji'`` then the ``'text'`` param must be a
            valid emoji string, for example ``':snoo:'``.
        :param max_emojis: (int) Maximum emojis in the flair
            (Reddit defaults this value to 10).

        For example, to add an editable Redditor flair try:

        .. code-block:: python

           reddit.subreddit('NAME').flair.templates.add(
               css_class='praw', text_editable=True)

        """
        self._add(
            text,
            css_class=css_class,
            text_editable=text_editable,
            is_link=False,
            background_color=background_color,
            text_color=text_color,
            mod_only=mod_only,
            allowable_content=allowable_content,
            max_emojis=max_emojis,
        )

    def clear(self):
        """Remove all Redditor flair templates from the subreddit.

        For example:

        .. code-block:: python

           reddit.subreddit('NAME').flair.templates.clear()

        """
        self._clear(is_link=False)
