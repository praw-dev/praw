"""Provide the SubredditFlairTemplates class."""

from .....const import API_PATH
from .....exceptions import InvalidFlairTemplateID


class SubredditFlairTemplates:
    """Provide functions to interact with a Subreddit's flair templates."""

    @staticmethod
    def flair_type(is_link):
        """Return LINK_FLAIR or USER_FLAIR depending on ``is_link`` value."""
        return "LINK_FLAIR" if is_link else "USER_FLAIR"

    def __init__(self, subreddit):
        """Create a SubredditFlairTemplate instance.

        :param subreddit: The subreddit whose flair templates to work with.

        .. note:: This class should not be initialized directly. Instead obtain
           an instance via:
           ``reddit.subreddit('subreddit_name').flair.templates`` or
           ``reddit.subreddit('subreddit_name').flair.link_templates``.

        """
        self.subreddit = subreddit

    def __iter__(self):
        """Abstract method to return flair templates."""
        raise NotImplementedError()

    def _add(
        self,
        text,
        css_class="",
        text_editable=False,
        is_link=None,
        background_color=None,
        text_color=None,
        mod_only=None,
        allowable_content=None,
        max_emojis=None,
    ):
        url = API_PATH["flairtemplate_v2"].format(subreddit=self.subreddit)
        data = {
            "allowable_content": allowable_content,
            "background_color": background_color,
            "css_class": css_class,
            "flair_type": self.flair_type(is_link),
            "max_emojis": max_emojis,
            "mod_only": bool(mod_only),
            "text": text,
            "text_color": text_color,
            "text_editable": bool(text_editable),
        }
        self.subreddit._reddit.post(url, data=data)

    def _clear(self, is_link=None):
        url = API_PATH["flairtemplateclear"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(
            url, data={"flair_type": self.flair_type(is_link)}
        )

    def delete(self, template_id):
        """Remove a flair template provided by ``template_id``.

        For example, to delete the first Redditor flair template listed, try:

        .. code-block:: python

           template_info = list(subreddit.flair.templates)[0]
           subreddit.flair.templates.delete(template_info['id'])

        """
        url = API_PATH["flairtemplatedelete"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(
            url, data={"flair_template_id": template_id}
        )

    def update(
        self,
        template_id,
        text=None,
        css_class=None,
        text_editable=None,
        background_color=None,
        text_color=None,
        mod_only=None,
        allowable_content=None,
        max_emojis=None,
        fetch=True,
    ):
        """Update the flair template provided by ``template_id``.

        :param template_id: The flair template to update. If not valid then
            an exception will be thrown.
        :param text: The flair template's new text (required).
        :param css_class: The flair template's new css_class (default: '').
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
        :param fetch: Whether or not PRAW will fetch existing information on
            the existing flair before updating (Default: True).

        .. warning:: If parameter ``fetch`` is set to ``False``, all parameters
             not provided will be reset to default (``None`` or ``False``)
             values.

        For example to make a user flair template text_editable, try:

        .. code-block:: python

           template_info = list(subreddit.flair.templates)[0]
           subreddit.flair.templates.update(
               template_info['id'],
               template_info['flair_text'],
               text_editable=True)

        """
        url = API_PATH["flairtemplate_v2"].format(subreddit=self.subreddit)
        data = {
            "allowable_content": allowable_content,
            "background_color": background_color,
            "css_class": css_class,
            "flair_template_id": template_id,
            "max_emojis": max_emojis,
            "mod_only": mod_only,
            "text": text,
            "text_color": text_color,
            "text_editable": text_editable,
        }
        if fetch:
            _existing_data = [
                template
                for template in iter(self)
                if template["id"] == template_id
            ]
            if len(_existing_data) != 1:
                raise InvalidFlairTemplateID(template_id)
            else:
                existing_data = _existing_data[0]
                for key, value in existing_data.items():
                    if data.get(key) is None:
                        data[key] = value
        self.subreddit._reddit.post(url, data=data)
