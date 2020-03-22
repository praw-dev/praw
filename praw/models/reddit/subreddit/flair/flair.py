"""Provide the SubredditFlair class."""

from .....const import API_PATH
from .....util.cache import cachedproperty
from ....listing.generator import ListingGenerator
from .link import SubredditLinkFlairTemplates
from .redditor import SubredditRedditorFlairTemplates


class SubredditFlair:
    """Provide a set of functions to interact with a Subreddit's flair."""

    @cachedproperty
    def link_templates(self):
        """Provide an instance of :class:`.SubredditLinkFlairTemplates`.

        Use this attribute for interacting with a subreddit's link flair
        templates. For example to list all the link flair templates for a
        subreddit which you have the ``flair`` moderator permission on try:

        .. code-block:: python

           for template in reddit.subreddit('NAME').flair.link_templates:
               print(template)

        """
        return SubredditLinkFlairTemplates(self.subreddit)

    @cachedproperty
    def templates(self):
        """Provide an instance of :class:`.SubredditRedditorFlairTemplates`.

        Use this attribute for interacting with a subreddit's flair
        templates. For example to list all the flair templates for a subreddit
        which you have the ``flair`` moderator permission on try:

        .. code-block:: python

           for template in reddit.subreddit('NAME').flair.templates:
               print(template)

        """
        return SubredditRedditorFlairTemplates(self.subreddit)

    def __call__(self, redditor=None, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for Redditors and their flairs.

        :param redditor: When provided, yield at most a single
            :class:`~.Redditor` instance (default: None).

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        Usage:

        .. code-block:: python

           for flair in reddit.subreddit('NAME').flair(limit=None):
               print(flair)

        """
        self.subreddit.__class__._safely_add_arguments(
            generator_kwargs, "params", name=redditor
        )
        generator_kwargs.setdefault("limit", None)
        url = API_PATH["flairlist"].format(subreddit=self.subreddit)
        return ListingGenerator(
            self.subreddit._reddit, url, **generator_kwargs
        )

    def __init__(self, subreddit):
        """Create a SubredditFlair instance.

        :param subreddit: The subreddit whose flair to work with.

        """
        self.subreddit = subreddit

    def configure(
        self,
        position="right",
        self_assign=False,
        link_position="left",
        link_self_assign=False,
        **settings
    ):
        """Update the subreddit's flair configuration.

        :param position: One of left, right, or False to disable (default:
            right).
        :param self_assign: (boolean) Permit self assignment of user flair
            (default: False).
        :param link_position: One of left, right, or False to disable
            (default: left).
        :param link_self_assign: (boolean) Permit self assignment
               of link flair (default: False).

        Additional keyword arguments can be provided to handle new settings as
        Reddit introduces them.

        """
        data = {
            "flair_enabled": bool(position),
            "flair_position": position or "right",
            "flair_self_assign_enabled": self_assign,
            "link_flair_position": link_position or "",
            "link_flair_self_assign_enabled": link_self_assign,
        }
        data.update(settings)
        url = API_PATH["flairconfig"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def delete(self, redditor):
        """Delete flair for a Redditor.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.

        .. note:: To delete the flair of many Redditors at once, please see
                  :meth:`~praw.models.reddit.subreddit.SubredditFlair.update`.

        """
        url = API_PATH["deleteflair"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data={"name": str(redditor)})

    def delete_all(self):
        """Delete all Redditor flair in the Subreddit.

        :returns: List of dictionaries indicating the success or failure of
            each delete.

        """
        return self.update(x["user"] for x in self())

    def set(self, redditor, text="", css_class="", flair_template_id=None):
        """Set flair for a Redditor.

        :param redditor: (Required) A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param text: The flair text to associate with the Redditor or
            Submission (default: '').
        :param css_class: The css class to associate with the flair html
            (default: ''). Use either this or ``flair_template_id``.
        :param flair_template_id: The ID of the flair template to be used
            (default: ``None``). Use either this or ``css_class``.

        This method can only be used by an authenticated user who is a
        moderator of the associated Subreddit.

        For example:

        .. code-block:: python

           reddit.subreddit('redditdev').flair.set('bboe', 'PRAW author',
                                                   css_class='mods')
           template = '6bd28436-1aa7-11e9-9902-0e05ab0fad46'
           reddit.subreddit('redditdev').flair.set('spez', 'Reddit CEO',
                                                   flair_template_id=template)

        """
        if css_class and flair_template_id is not None:
            raise TypeError(
                "Parameter `css_class` cannot be used in "
                "conjunction with `flair_template_id`."
            )
        data = {"name": str(redditor), "text": text}
        if flair_template_id is not None:
            data["flair_template_id"] = flair_template_id
            url = API_PATH["select_flair"].format(subreddit=self.subreddit)
        else:
            data["css_class"] = css_class
            url = API_PATH["flair"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def update(self, flair_list, text="", css_class=""):
        """Set or clear the flair for many Redditors at once.

        :param flair_list: Each item in this list should be either: the name of
            a Redditor, an instance of :class:`.Redditor`, or a dictionary
            mapping keys ``user``, ``flair_text``, and ``flair_css_class`` to
            their respective values. The ``user`` key should map to a Redditor,
            as described above. When a dictionary isn't provided, or the
            dictionary is missing one of ``flair_text``, or ``flair_css_class``
            attributes the default values will come from the the following
            arguments.

        :param text: The flair text to use when not explicitly provided in
            ``flair_list`` (default: '').
        :param css_class: The css class to use when not explicitly provided in
            ``flair_list`` (default: '').
        :returns: List of dictionaries indicating the success or failure of
            each update.

        For example to clear the flair text, and set the ``praw`` flair css
        class on a few users try:

        .. code-block:: python

           subreddit.flair.update(['bboe', 'spez', 'spladug'],
                                  css_class='praw')

        """
        lines = []
        for item in flair_list:
            if isinstance(item, dict):
                fmt_data = (
                    str(item["user"]),
                    item.get("flair_text", text),
                    item.get("flair_css_class", css_class),
                )
            else:
                fmt_data = (str(item), text, css_class)
            lines.append('"{}","{}","{}"'.format(*fmt_data))

        response = []
        url = API_PATH["flaircsv"].format(subreddit=self.subreddit)
        while lines:
            data = {"flair_csv": "\n".join(lines[:100])}
            response.extend(self.subreddit._reddit.post(url, data=data))
            lines = lines[100:]
        return response
