"""Provide the SubredditModeration class."""

from ....const import API_PATH
from ....util.cache import cachedproperty
from ...listing.generator import ListingGenerator
from ..base import RedditBase
from ..removal_reasons import SubredditRemovalReasons
from .moderation_stream import SubredditModerationStream


class SubredditModeration:
    """Provides a set of moderation functions to a Subreddit.

    For example, to accept a moderation invite from subreddit ``r/test``:

    .. code-block:: python

        reddit.subreddit('test').mod.accept_invite()

    """

    @staticmethod
    def _handle_only(only, generator_kwargs):
        if only is not None:
            if only == "submissions":
                only = "links"
            RedditBase._safely_add_arguments(
                generator_kwargs, "params", only=only
            )

    def __init__(self, subreddit):
        """Create a SubredditModeration instance.

        :param subreddit: The subreddit to moderate.

        """
        self.subreddit = subreddit
        self._stream = None

    def accept_invite(self):
        """Accept an invitation as a moderator of the community."""
        url = API_PATH["accept_mod_invite"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url)

    def edited(self, only=None, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for edited comments and submissions.

        :param only: If specified, one of ``'comments'``, or ``'submissions'``
            to yield only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print all items in the edited queue try:

        .. code-block:: python

           for item in reddit.subreddit('mod').mod.edited(limit=None):
               print(item)

        """
        self._handle_only(only, generator_kwargs)
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_edited"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    def inbox(self, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for moderator messages.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        See ``unread`` for unread moderator messages.

        To print the last 5 moderator mail messages and their replies, try:

        .. code-block:: python

           for message in reddit.subreddit('mod').mod.inbox(limit=5):
               print("From: {}, Body: {}".format(message.author, message.body))
               for reply in message.replies:
                   print("From: {}, Body: {}".format(reply.author, reply.body))

        """
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["moderator_messages"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    def log(self, action=None, mod=None, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for moderator log entries.

        :param action: If given, only return log entries for the specified
            action.
        :param mod: If given, only return log entries for actions made by the
            passed in Redditor.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print the moderator and subreddit of the last 5 modlog entries try:

        .. code-block:: python

           for log in reddit.subreddit('mod').mod.log(limit=5):
               print("Mod: {}, Subreddit: {}".format(log.mod, log.subreddit))

        """
        params = {"mod": str(mod) if mod else mod, "type": action}
        self.subreddit.__class__._safely_add_arguments(
            generator_kwargs, "params", **params
        )
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_log"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    def modqueue(self, only=None, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for modqueue items.

        :param only: If specified, one of ``'comments'``, or ``'submissions'``
            to yield only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print all modqueue items try:

        .. code-block:: python

           for item in reddit.subreddit('mod').mod.modqueue(limit=None):
               print(item)

        """
        self._handle_only(only, generator_kwargs)
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_modqueue"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    @property
    def stream(self):
        """Provide an instance of :class:`.SubredditModerationStream`.

        Streams can be used to indefinitely retrieve Moderator only items from
        :class:`.SubredditModeration` made to moderated subreddits, like:

        .. code-block:: python

           for log in reddit.subreddit('mod').mod.stream.log():
               print("Mod: {}, Subreddit: {}".format(log.mod, log.subreddit))

        """
        if self._stream is None:
            self._stream = SubredditModerationStream(self.subreddit)
        return self._stream

    @cachedproperty
    def removal_reasons(self):
        """Provide an instance of :class:`.SubredditRemovalReasons`.

        Use this attribute for interacting with a subreddit's removal reasons.
        For example to list all the removal reasons for a subreddit which you
        have the ``posts`` moderator permission on, try:

        .. code-block:: python

           for removal_reason in reddit.subreddit('NAME').mod.removal_reasons:
               print(removal_reason)

        A single removal reason can be lazily retrieved via:

        .. code-block:: python

           reddit.subreddit('NAME').mod.removal_reasons['reason_id']

        .. note:: Attempting to access attributes of an nonexistent removal
           reason will result in a :class:`.ClientException`.

        """
        return SubredditRemovalReasons(self.subreddit)

    def reports(self, only=None, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for reported comments and submissions.

        :param only: If specified, one of ``'comments'``, or ``'submissions'``
            to yield only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print the user and mod report reasons in the report queue try:

        .. code-block:: python

           for reported_item in reddit.subreddit('mod').mod.reports():
               print("User Reports: {}".format(reported_item.user_reports))
               print("Mod Reports: {}".format(reported_item.mod_reports))

        """
        self._handle_only(only, generator_kwargs)
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_reports"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    def settings(self):
        """Return a dictionary of the subreddit's current settings."""
        url = API_PATH["subreddit_settings"].format(subreddit=self.subreddit)
        return self.subreddit._reddit.get(url)["data"]

    def spam(self, only=None, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for spam comments and submissions.

        :param only: If specified, one of ``'comments'``, or ``'submissions'``
            to yield only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print the items in the spam queue try:

        .. code-block:: python

           for item in reddit.subreddit('mod').mod.spam():
               print(item)

        """
        self._handle_only(only, generator_kwargs)
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_spam"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    def unmoderated(self, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for unmoderated submissions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print the items in the unmoderated queue try:

        .. code-block:: python

           for item in reddit.subreddit('mod').mod.unmoderated():
               print(item)

        """
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_unmoderated"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    def unread(self, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for unread moderator messages.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        See ``inbox`` for all messages.

        To print the mail in the unread modmail queue try:

        .. code-block:: python

           for message in reddit.subreddit('mod').mod.unread():
               print("From: {}, To: {}".format(message.author, message.dest))

        """
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["moderator_unread"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    def update(self, **settings):
        """Update the subreddit's settings.

        :param all_original_content: Mandate all submissions to be original
            content only.
        :param allow_chat_post_creation: Allow users to create chat
            submissions.
        :param allow_images: Allow users to upload images using the native
            image hosting.
        :param allow_polls: Allow users to post polls to the subreddit.
        :param allow_post_crossposts: Allow users to crosspost submissions from
            other subreddits.
        :param allow_top: Allow the subreddit to appear on ``r/all`` as well
            as the default and trending lists.
        :param allow_videos: Allow users to upload videos using the native
            image hosting.
        :param collapse_deleted_comments: Collapse deleted and removed comments
            on comments pages by default.
        :param crowd_control_chat_level: Controls the crowd control level for
            chat rooms. Goes from 0-3.
        :param crowd_control_level: Controls the crowd control level for
            submissions. Goes from 0-3.
        :param crowd_control_mode: Enables/disables crowd control.
        :param comment_score_hide_mins: The number of minutes to hide comment
            scores.
        :param description: Shown in the sidebar of your subreddit.
        :param disable_contributor_requests: Specifies whether redditors may
            send automated modmail messages requesting approval as a submitter.
        :param exclude_banned_modqueue: Exclude posts by site-wide banned users
            from modqueue/unmoderated.
        :param free_form_reports: Allow users to specify custom reasons in the
            report menu.
        :param header_hover_text: The text seen when hovering over the snoo.
        :param hide_ads: Don't show ads within this subreddit. Only applies to
            Premium-user only subreddits.
        :param key_color: A 6-digit rgb hex color (e.g. ``'#AABBCC'``), used as
            a thematic color for your subreddit on mobile.
        :param lang: A valid IETF language tag (underscore separated).
        :param link_type: The types of submissions users can make.
            One of ``any``, ``link``, ``self``.
        :param original_content_tag_enabled: Enables the use of the
            ``original content`` label for submissions.
        :param over_18: Viewers must be over 18 years old (i.e. NSFW).
        :param public_description: Public description blurb. Appears in search
            results and on the landing page for private subreddits.
        :param public_traffic: Make the traffic stats page public.
        :param restrict_commenting: Specifies whether approved users have the
            ability to comment.
        :param restrict_posting: Specifies whether approved users have the
            ability to submit posts.
        :param show_media: Show thumbnails on submissions.
        :param show_media_preview: Expand media previews on comments pages.
        :param spam_comments: Spam filter strength for comments.
            One of ``all``, ``low``, ``high``.
        :param spam_links: Spam filter strength for links.
            One of ``all``, ``low``, ``high``.
        :param spam_selfposts: Spam filter strength for selfposts.
            One of ``all``, ``low``, ``high``.
        :param spoilers_enabled: Enable marking posts as containing spoilers.
        :param submit_link_label: Custom label for submit link button
            (None for default).
        :param submit_text: Text to show on submission page.
        :param submit_text_label: Custom label for submit text post button
            (None for default).
        :param subreddit_type: One of ``archived``, ``employees_only``,
            ``gold_only``, ``gold_restricted``, ``private``, ``public``,
            ``restricted``.
        :param suggested_comment_sort: All comment threads will use this
            sorting method by default. Leave None, or choose one of
            ``confidence``, ``controversial``, ``live``, ``new``, ``old``,
            ``qa``, ``random``, ``top``.
        :param title: The title of the subreddit.
        :param welcome_message_enabled: Enables the subreddit welcome message.
        :param welcome_message_text: The text to be used as a welcome message.
            A welcome message is sent to all new subscribers by a Reddit bot.
        :param wiki_edit_age: Account age, in days, required to edit and create
            wiki pages.
        :param wiki_edit_karma: Subreddit karma required to edit and create
            wiki pages.

        Additional keyword arguments can be provided to handle new settings as
        Reddit introduces them.

        Settings that are documented here and aren't explicitly set by you in a
        call to :meth:`.SubredditModeration.update` should retain their current
        value. If they do not please file a bug.

        .. warning:: Undocumented settings, or settings that were very recently
                     documented, may not retain their current value when
                     updating. This often occurs when Reddit adds a new setting
                     but forgets to add that setting to the API endpoint that
                     is used to fetch the current settings.

        """
        current_settings = self.settings()
        fullname = current_settings.pop("subreddit_id")

        # These attributes come out using different names than they go in.
        remap = {
            "allow_top": "default_set",
            "lang": "language",
            "link_type": "content_options",
        }
        for new, old in remap.items():
            current_settings[new] = current_settings.pop(old)

        current_settings.update(settings)
        return self.subreddit.__class__._create_or_update(
            _reddit=self.subreddit._reddit, sr=fullname, **current_settings
        )
