"""Provide the SubredditModerationStream class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from praw.const import API_PATH
from praw.models.listing.generator import ListingGenerator
from praw.models.reddit.base import RedditBase
from praw.models.reddit.removal_reasons import SubredditRemovalReasons
from praw.models.util import stream_generator
from praw.util import cachedproperty

if TYPE_CHECKING:
    from collections.abc import Iterator

    from praw import models
    from praw.models.reddit.modmail import ModmailConversation


class SubredditModeration:
    """Provides a set of moderation functions to a :class:`.Subreddit`.

    For example, to accept a moderation invite from r/test:

    .. code-block:: python

        reddit.subreddit("test").mod.accept_invite()

    """

    @staticmethod
    def _handle_only(*, generator_kwargs: dict[str, Any], only: str | None) -> None:
        if only is not None:
            if only == "submissions":
                only = "links"
            RedditBase._safely_add_arguments(arguments=generator_kwargs, key="params", only=only)

    @cachedproperty
    def notes(self) -> models.SubredditModNotes:
        """Provide an instance of :class:`.SubredditModNotes`.

        This provides an interface for managing moderator notes for this subreddit.

        For example, all the notes for u/spez in r/test can be iterated through like so:

        .. code-block:: python

            subreddit = reddit.subreddit("test")

            for note in subreddit.mod.notes.redditors("spez"):
                print(f"{note.label}: {note.note}")

        """
        from praw.models.mod_notes import SubredditModNotes  # noqa: PLC0415

        return SubredditModNotes(self.subreddit._reddit, subreddit=self.subreddit)

    @cachedproperty
    def removal_reasons(self) -> SubredditRemovalReasons:
        """Provide an instance of :class:`.SubredditRemovalReasons`.

        Use this attribute for interacting with a :class:`.Subreddit`'s removal reasons.
        For example to list all the removal reasons for a subreddit which you have the
        ``posts`` moderator permission on, try:

        .. code-block:: python

            for removal_reason in reddit.subreddit("test").mod.removal_reasons:
                print(removal_reason)

        A single removal reason can be lazily retrieved via:

        .. code-block:: python

            reddit.subreddit("test").mod.removal_reasons["reason_id"]

        .. note::

            Attempting to access attributes of a nonexistent removal reason will result
            in a :class:`.ClientException`.

        """
        return SubredditRemovalReasons(self.subreddit)

    @cachedproperty
    def stream(self) -> SubredditModerationStream:
        """Provide an instance of :class:`.SubredditModerationStream`.

        Streams can be used to indefinitely retrieve Moderator only items from
        :class:`.SubredditModeration` made to moderated subreddits, like:

        .. code-block:: python

            for log in reddit.subreddit("mod").mod.stream.log():
                print(f"Mod: {log.mod}, Subreddit: {log.subreddit}")

        """
        return SubredditModerationStream(self.subreddit)

    def __init__(self, subreddit: models.Subreddit) -> None:
        """Initialize a :class:`.SubredditModeration` instance.

        :param subreddit: The subreddit to moderate.

        """
        self.subreddit = subreddit
        self._stream = None

    def accept_invite(self) -> None:
        """Accept an invitation as a moderator of the community."""
        url = API_PATH["accept_mod_invite"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url)

    def edited(
        self, *, only: str | None = None, **generator_kwargs: Any
    ) -> Iterator[models.Comment | models.Submission]:
        """Return a :class:`.ListingGenerator` for edited comments and submissions.

        :param only: If specified, one of ``"comments"`` or ``"submissions"`` to yield
            only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print all items in the edited queue try:

        .. code-block:: python

            for item in reddit.subreddit("mod").mod.edited(limit=None):
                print(item)

        """
        self._handle_only(generator_kwargs=generator_kwargs, only=only)
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_edited"].format(subreddit=self.subreddit),
            **generator_kwargs,
        )

    def log(
        self,
        *,
        action: str | None = None,
        mod: models.Redditor | str | None = None,
        **generator_kwargs: Any,
    ) -> Iterator[models.ModAction]:
        """Return a :class:`.ListingGenerator` for moderator log entries.

        :param action: If given, only return log entries for the specified action.
        :param mod: If given, only return log entries for actions made by the passed in
            redditor.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print the moderator and subreddit of the last 5 modlog entries try:

        .. code-block:: python

            for log in reddit.subreddit("mod").mod.log(limit=5):
                print(f"Mod: {log.mod}, Subreddit: {log.subreddit}")

        """
        params = {"mod": str(mod) if mod else mod, "type": action}
        RedditBase._safely_add_arguments(arguments=generator_kwargs, key="params", **params)
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_log"].format(subreddit=self.subreddit),
            **generator_kwargs,
        )

    def modqueue(
        self, *, only: str | None = None, **generator_kwargs: Any
    ) -> Iterator[models.Submission | models.Comment]:
        """Return a :class:`.ListingGenerator` for modqueue items.

        :param only: If specified, one of ``"comments"`` or ``"submissions"`` to yield
            only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print all modqueue items try:

        .. code-block:: python

            for item in reddit.subreddit("mod").mod.modqueue(limit=None):
                print(item)

        """
        self._handle_only(generator_kwargs=generator_kwargs, only=only)
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_modqueue"].format(subreddit=self.subreddit),
            **generator_kwargs,
        )

    def reports(
        self, *, only: str | None = None, **generator_kwargs: Any
    ) -> Iterator[models.Submission | models.Comment]:
        """Return a :class:`.ListingGenerator` for reported comments and submissions.

        :param only: If specified, one of ``"comments"`` or ``"submissions"`` to yield
            only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print the user and mod report reasons in the report queue try:

        .. code-block:: python

            for reported_item in reddit.subreddit("mod").mod.reports():
                print(f"User Reports: {reported_item.user_reports}")
                print(f"Mod Reports: {reported_item.mod_reports}")

        """
        self._handle_only(generator_kwargs=generator_kwargs, only=only)
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_reports"].format(subreddit=self.subreddit),
            **generator_kwargs,
        )

    def settings(self) -> dict[str, str | int | bool]:
        """Return a dictionary of the :class:`.Subreddit`'s current settings."""
        url = API_PATH["subreddit_settings"].format(subreddit=self.subreddit)
        return self.subreddit._reddit.get(url)["data"]

    def spam(self, *, only: str | None = None, **generator_kwargs: Any) -> Iterator[models.Submission | models.Comment]:
        """Return a :class:`.ListingGenerator` for spam comments and submissions.

        :param only: If specified, one of ``"comments"`` or ``"submissions"`` to yield
            only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print the items in the spam queue try:

        .. code-block:: python

            for item in reddit.subreddit("mod").mod.spam():
                print(item)

        """
        self._handle_only(generator_kwargs=generator_kwargs, only=only)
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_spam"].format(subreddit=self.subreddit),
            **generator_kwargs,
        )

    def unmoderated(self, **generator_kwargs: Any) -> Iterator[models.Submission]:
        """Return a :class:`.ListingGenerator` for unmoderated submissions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print the items in the unmoderated queue try:

        .. code-block:: python

            for item in reddit.subreddit("mod").mod.unmoderated():
                print(item)

        """
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_unmoderated"].format(subreddit=self.subreddit),
            **generator_kwargs,
        )

    def update(self, **settings: str | int | bool) -> dict[str, str | int | bool]:
        """Update the :class:`.Subreddit`'s settings.

        See https://www.reddit.com/dev/api#POST_api_site_admin for the full list.

        :param all_original_content: Mandate all submissions to be original content
            only.
        :param allow_chat_post_creation: Allow users to create chat submissions.
        :param allow_images: Allow users to upload images using the native image
            hosting.
        :param allow_polls: Allow users to post polls to the subreddit.
        :param allow_post_crossposts: Allow users to crosspost submissions from other
            subreddits.
        :param allow_videos: Allow users to upload videos using the native image
            hosting.
        :param collapse_deleted_comments: Collapse deleted and removed comments on
            comments pages by default.
        :param comment_score_hide_mins: The number of minutes to hide comment scores.
        :param content_options: The types of submissions users can make. One of
            ``"any"``, ``"link"``, or ``"self"``.
        :param crowd_control_chat_level: Controls the crowd control level for chat
            rooms. Goes from 0-3.
        :param crowd_control_level: Controls the crowd control level for submissions.
            Goes from 0-3.
        :param crowd_control_mode: Enables/disables crowd control.
        :param default_set: Allow the subreddit to appear on r/all as well as the
            default and trending lists.
        :param disable_contributor_requests: Specifies whether redditors may send
            automated modmail messages requesting approval as a submitter.
        :param exclude_banned_modqueue: Exclude posts by site-wide banned users from
            modqueue/unmoderated.
        :param free_form_reports: Allow users to specify custom reasons in the report
            menu.
        :param header_hover_text: The text seen when hovering over the snoo.
        :param hide_ads: Don't show ads within this subreddit. Only applies to
            Premium-user only subreddits.
        :param key_color: A 6-digit rgb hex color (e.g., ``"#AABBCC"``), used as a
            thematic color for your subreddit on mobile.
        :param language: A valid IETF language tag (underscore separated).
        :param original_content_tag_enabled: Enables the use of the ``original content``
            label for submissions.
        :param over_18: Viewers must be over 18 years old (i.e., NSFW).
        :param public_description: Public description blurb. Appears in search results
            and on the landing page for private subreddits.
        :param restrict_commenting: Specifies whether approved users have the ability to
            comment.
        :param restrict_posting: Specifies whether approved users have the ability to
            submit posts.
        :param show_media: Show thumbnails on submissions.
        :param show_media_preview: Expand media previews on comments pages.
        :param spam_comments: Spam filter strength for comments. One of ``"all"``,
            ``"low"``, or ``"high"``.
        :param spam_links: Spam filter strength for links. One of ``"all"``, ``"low"``,
            or ``"high"``.
        :param spam_selfposts: Spam filter strength for selfposts. One of ``"all"``,
            ``"low"``, or ``"high"``.
        :param spoilers_enabled: Enable marking posts as containing spoilers.
        :param submit_link_label: Custom label for submit link button (``None`` for
            default).
        :param submit_text: Text to show on submission page.
        :param submit_text_label: Custom label for submit text post button (``None`` for
            default).
        :param subreddit_type: One of ``"archived"``, ``"employees_only"``,
            ``"gold_only"``, ``gold_restricted``, ``"private"``, ``"public"``, or
            ``"restricted"``.
        :param suggested_comment_sort: All comment threads will use this sorting method
            by default. Leave ``None``, or choose one of ``"confidence"``,
            ``"controversial"``, ``"live"``, ``"new"``, ``"old"``, ``"qa"``,
            ``"random"``, or ``"top"``.
        :param title: The title of the subreddit.
        :param welcome_message_enabled: Enables the subreddit welcome message.
        :param welcome_message_text: The text to be used as a welcome message. A welcome
            message is sent to all new subscribers by a Reddit bot.
        :param wiki_edit_age: Account age, in days, required to edit and create wiki
            pages.
        :param wiki_edit_karma: Subreddit karma required to edit and create wiki pages.
        :param wikimode: One of ``"anyone"``, ``"disabled"``, or ``"modonly"``.

        .. note::

            Updating the subreddit sidebar on old reddit (``description``) is no longer
            supported using this method. You can update the sidebar by editing the
            ``"config/sidebar"`` wiki page. For example:

            .. code-block:: python

                sidebar = reddit.subreddit("test").wiki["config/sidebar"]
                sidebar.edit(content="new sidebar content")

        Additional keyword arguments can be provided to handle new settings as Reddit
        introduces them.

        Settings that are documented here and aren't explicitly set by you in a call to
        :meth:`.SubredditModeration.update` should retain their current value. If they
        do not, please file a bug.

        """
        # These attributes come out using different names than they go in.
        remap = {
            "content_options": "link_type",
            "default_set": "allow_top",
            "header_hover_text": "header_title",
            "language": "lang",
            "subreddit_type": "type",
        }
        settings = {remap.get(key, key): value for key, value in settings.items()}
        settings["sr"] = self.subreddit.fullname
        return self.subreddit._reddit.patch(API_PATH["update_settings"], json=settings)


class SubredditModerationStream:
    """Provides moderator streams."""

    def __init__(self, subreddit: models.Subreddit) -> None:
        """Initialize a :class:`.SubredditModerationStream` instance.

        :param subreddit: The moderated subreddit associated with the streams.

        """
        self.subreddit = subreddit

    def edited(self, *, only: str | None = None, **stream_options: Any) -> Iterator[models.Comment | models.Submission]:
        """Yield edited comments and submissions as they become available.

        :param only: If specified, one of ``"comments"`` or ``"submissions"`` to yield
            only results of that type.

        Keyword arguments are passed to :func:`.stream_generator`.

        For example, to retrieve all new edited submissions/comments made to all
        moderated subreddits, try:

        .. code-block:: python

            for item in reddit.subreddit("mod").mod.stream.edited():
                print(item)

        """
        return stream_generator(self.subreddit.mod.edited, only=only, **stream_options)

    def log(
        self,
        *,
        action: str | None = None,
        mod: str | models.Redditor | None = None,
        **stream_options: Any,
    ) -> Iterator[models.ModAction]:
        """Yield moderator log entries as they become available.

        :param action: If given, only return log entries for the specified action.
        :param mod: If given, only return log entries for actions made by the passed in
            redditor.

        For example, to retrieve all new mod actions made to all moderated subreddits,
        try:

        .. code-block:: python

            for log in reddit.subreddit("mod").mod.stream.log():
                print(f"Mod: {log.mod}, Subreddit: {log.subreddit}")

        """
        return stream_generator(
            self.subreddit.mod.log,
            action=action,
            attribute_name="id",
            mod=mod,
            **stream_options,
        )

    def modmail_conversations(
        self,
        *,
        other_subreddits: list[models.Subreddit] | None = None,
        sort: str | None = None,
        state: str | None = None,
        **stream_options: Any,
    ) -> Iterator[ModmailConversation]:
        """Yield new-modmail conversations as they become available.

        :param other_subreddits: A list of :class:`.Subreddit` instances for which to
            fetch conversations (default: ``None``).
        :param sort: Can be one of: ``"mod"``, ``"recent"``, ``"unread"``, or ``"user"``
            (default: ``"recent"``).
        :param state: Can be one of: ``"all"``, ``"appeals"``, ``"archived"``,
            ``"default"``, ``"highlighted"``, ``"inbox"``, ``"inprogress"``,
            ``"join_requests"``, ``"mod"``, ``"new"``, or ``"notifications"`` (default:
            ``"all"``). ``"all"`` does not include mod or archived conversations.
            ``"inbox"`` does not include appeals conversations.

        Keyword arguments are passed to :func:`.stream_generator`.

        To print new mail in the unread modmail queue try:

        .. code-block:: python

            subreddit = reddit.subreddit("all")
            for message in subreddit.mod.stream.modmail_conversations():
                print(f"From: {message.owner}, To: {message.participant}")

        """
        if self.subreddit == "mod":
            self.subreddit = self.subreddit._reddit.subreddit("all")
        return stream_generator(
            self.subreddit.modmail.conversations,
            attribute_name="id",
            exclude_before=True,
            other_subreddits=other_subreddits,
            sort=sort,
            state=state,
            **stream_options,
        )

    def modqueue(
        self, *, only: str | None = None, **stream_options: Any
    ) -> Iterator[models.Comment | models.Submission]:
        r"""Yield :class:`.Comment`\ s and :class:`.Submission`\ s in the modqueue as they become available.

        :param only: If specified, one of ``"comments"`` or ``"submissions"`` to yield
            only results of that type.

        Keyword arguments are passed to :func:`.stream_generator`.

        To print all new modqueue items try:

        .. code-block:: python

            for item in reddit.subreddit("mod").mod.stream.modqueue():
                print(item)

        """
        return stream_generator(self.subreddit.mod.modqueue, only=only, **stream_options)

    def reports(
        self, *, only: str | None = None, **stream_options: Any
    ) -> Iterator[models.Comment | models.Submission]:
        r"""Yield reported :class:`.Comment`\ s and :class:`.Submission`\ s as they become available.

        :param only: If specified, one of ``"comments"`` or ``"submissions"`` to yield
            only results of that type.

        Keyword arguments are passed to :func:`.stream_generator`.

        To print new user and mod report reasons in the report queue try:

        .. code-block:: python

            for item in reddit.subreddit("mod").mod.stream.reports():
                print(item)

        """
        return stream_generator(self.subreddit.mod.reports, only=only, **stream_options)

    def spam(self, *, only: str | None = None, **stream_options: Any) -> Iterator[models.Comment | models.Submission]:
        r"""Yield spam :class:`.Comment`\ s and :class:`.Submission`\ s as they become available.

        :param only: If specified, one of ``"comments"`` or ``"submissions"`` to yield
            only results of that type.

        Keyword arguments are passed to :func:`.stream_generator`.

        To print new items in the spam queue try:

        .. code-block:: python

            for item in reddit.subreddit("mod").mod.stream.spam():
                print(item)

        """
        return stream_generator(self.subreddit.mod.spam, only=only, **stream_options)

    def unmoderated(self, **stream_options: Any) -> Iterator[models.Submission]:
        r"""Yield unmoderated :class:`.Submission`\ s as they become available.

        Keyword arguments are passed to :func:`.stream_generator`.

        To print new items in the unmoderated queue try:

        .. code-block:: python

            for item in reddit.subreddit("mod").mod.stream.unmoderated():
                print(item)

        """
        return stream_generator(self.subreddit.mod.unmoderated, **stream_options)
