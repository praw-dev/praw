"""Provide the SubredditLinkFlairTemplates class."""

from .....const import API_PATH
from .templates import SubredditFlairTemplates


class SubredditLinkFlairTemplates(SubredditFlairTemplates):
    """Provide functions to interact with link flair templates."""

    def __iter__(self):
        """Iterate through the link flair templates.

        For example:

        .. code-block:: python

           for template in reddit.subreddit('NAME').flair.link_templates:
               print(template)

        """
        url = API_PATH["link_flair"].format(subreddit=self.subreddit)
        for template in self.subreddit._reddit.get(url):
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
        """Add a link flair template to the associated subreddit.

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

        For example, to add an editable link flair try:

        .. code-block:: python

           reddit.subreddit('NAME').flair.link_templates.add(
               css_class='praw', text_editable=True)

        """
        self._add(
            text,
            css_class=css_class,
            text_editable=text_editable,
            is_link=True,
            background_color=background_color,
            text_color=text_color,
            mod_only=mod_only,
            allowable_content=allowable_content,
            max_emojis=max_emojis,
        )

    def clear(self):
        """Remove all link flair templates from the subreddit.

        For example:

        .. code-block:: python

           reddit.subreddit('NAME').flair.link_templates.clear()

        """
        self._clear(is_link=True)
