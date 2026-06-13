.. _praw8_migration:

#####################
 Migrating to PRAW 8
#####################

PRAW 8 completes the deprecation cycle started during the 7.x series. This guide covers
every removed or changed item, with examples showing how to update your code.

************************
 Python Version Support
************************

PRAW 8 requires Python 3.10 or newer. Support for Python 3.8 and 3.9, both of which are
end-of-life, has been dropped, and support for Python 3.13 and 3.14 has been added.

*********************************
 Dependency and Behavior Changes
*********************************

PRAW 8 raises several dependency floors: it now requires ``prawcore >=3.2, <4`` (for its
public :class:`!Session` and authorizer accessors) and ``update_checker >=1.0, <2``, and
it constrains ``websocket-client`` to ``<2``. These requirements are resolved
automatically when you install or upgrade PRAW; no code changes are required.

PRAW now ships a :PEP:`561` ``py.typed`` marker, so downstream projects can type check
against PRAW's inline annotations. This is additive and does not change runtime
behavior.

PRAW now warns at initialization if a ``praw.ini`` file in the current working directory
sets the ``oauth_url`` or ``reddit_url`` endpoint, since such a file can redirect
credentials to an untrusted host. If you intentionally override these endpoints (for
example, to test against a mock server), silence the warning by setting the
``PRAW_ALLOW_ENDPOINT_OVERRIDE`` environment variable.

Changing how a :class:`.Submission` is fetched after the fact now raises
:class:`.ClientException` instead of logging a warning. Set the ``comment_sort`` and
``comment_limit`` attributes, and call :meth:`.Submission.add_fetch_param`, before the
submission is fetched -- that is, before accessing any of its attributes. The
``warn_comment_sort`` and ``warn_additional_fetch_params`` configuration options, which
previously toggled these warnings, have been removed.

***************
 Media Uploads
***************

All methods that upload media now accept :class:`.Media` instances instead of file
paths. The relevant subclass depends on what is being uploaded: :class:`.PostMedia` for
submissions and inline media, :class:`.EmojiMedia` for emoji, :class:`.StylesheetImage`
and :class:`.StylesheetAsset` for stylesheet images, and :class:`.WidgetMedia` for
widget images.

A :class:`.Media` instance can be constructed from a file path, or from ``bytes``
content along with a ``name``, so media no longer has to be written to disk before
uploading:

.. code-block:: python

    from praw.models import PostMedia

    media_from_path = PostMedia("/path/to/image.png")
    media_from_bytes = PostMedia(image_bytes, "image.png")

Inline media
============

The ``path`` argument to :class:`.InlineMedia` (:class:`.InlineGif`,
:class:`.InlineImage`, and :class:`.InlineVideo`) has been replaced by ``media``, which
takes a :class:`.PostMedia` instance.

Old:

.. code-block:: python
    :class: code-old

    from praw.models import InlineImage

    image = InlineImage(caption="optional caption", path="/path/to/image.jpg")

New:

.. code-block:: python

    from praw.models import InlineImage, PostMedia

    image = InlineImage(caption="optional caption", media=PostMedia("/path/to/image.jpg"))

Emoji
=====

The ``image_path`` argument to :meth:`.SubredditEmoji.add` has been replaced by
``media``, which takes an :class:`.EmojiMedia` instance.

Old:

.. code-block:: python
    :class: code-old

    reddit.subreddit("test").emoji.add(image_path="emoji.png", name="emoji")

New:

.. code-block:: python

    from praw.models import EmojiMedia

    reddit.subreddit("test").emoji.add(media=EmojiMedia("emoji.png"), name="emoji")

Stylesheet images
=================

The ``image_path`` arguments to the :class:`.SubredditStylesheet` ``upload_*`` methods
have been replaced by ``media``, which must be passed positionally.
:meth:`.SubredditStylesheet.upload`, :meth:`.upload_header`,
:meth:`.upload_mobile_header`, and :meth:`.upload_mobile_icon` take a
:class:`.StylesheetImage` instance, while :meth:`.upload_banner`,
:meth:`.upload_banner_additional_image`, :meth:`.upload_banner_hover_image`, and
:meth:`.upload_mobile_banner` take a :class:`.StylesheetAsset` instance.

Old:

.. code-block:: python
    :class: code-old

    stylesheet = reddit.subreddit("test").stylesheet
    stylesheet.upload(image_path="img.png", name="smile")
    stylesheet.upload_banner("banner.png")

New:

.. code-block:: python

    from praw.models import StylesheetAsset, StylesheetImage

    stylesheet = reddit.subreddit("test").stylesheet
    stylesheet.upload(StylesheetImage("img.png"), name="smile")
    stylesheet.upload_banner(StylesheetAsset("banner.png"))

Widget images
=============

The ``file_path`` argument to :meth:`.SubredditWidgetsModeration.upload_image` has been
replaced by ``media``, which takes a :class:`.WidgetMedia` instance and must be passed
positionally.

Old:

.. code-block:: python
    :class: code-old

    image_url = reddit.subreddit("test").widgets.mod.upload_image("/path/to/image.jpg")

New:

.. code-block:: python

    from praw.models import WidgetMedia

    image_url = reddit.subreddit("test").widgets.mod.upload_image(
        WidgetMedia("/path/to/image.jpg")
    )

Other media upload changes
==========================

- An unknown media type now raises :class:`.ClientException` when uploading media,
  instead of falling back to JPEG.
- Media uploads to Reddit's S3 buckets now respect the configured ``timeout`` and raise
  ``prawcore.RequestException`` on transport errors, consistent with all other requests.
  Code that caught raw ``requests`` exceptions around media uploads should catch
  ``prawcore.RequestException`` instead.

***************************
 Unified ``submit`` method
***************************

``Subreddit.submit_gallery``, ``Subreddit.submit_image``, ``Subreddit.submit_poll``, and
``Subreddit.submit_video`` have been merged into :meth:`.Subreddit.submit`. The kind of
submission is selected with the ``gallery``, ``image``, ``poll``, ``url``, or ``video``
keyword argument. At least one of those, or ``selftext``, must be provided, and they are
mutually exclusive, while ``selftext`` may accompany any of them as optional
Markdown-formatted body text.

Submitting an image
===================

Old:

.. code-block:: python
    :class: code-old

    reddit.subreddit("test").submit_image("My Title", "/path/to/image.png")

New:

.. code-block:: python

    from praw.models import PostMedia

    reddit.subreddit("test").submit("My Title", image=PostMedia("/path/to/image.png"))

Submitting a video
==================

Video-specific options, such as a custom thumbnail or submitting the video as a
videogif, are provided by passing a ``dict`` instead of a bare :class:`.PostMedia`.

Old:

.. code-block:: python
    :class: code-old

    reddit.subreddit("test").submit_video(
        "My Title", "/path/to/video.mp4", thumbnail_path="/path/to/thumbnail.png"
    )

New:

.. code-block:: python

    from praw.models import PostMedia

    reddit.subreddit("test").submit(
        "My Title",
        video={
            "media": PostMedia("/path/to/video.mp4"),
            "thumbnail": PostMedia("/path/to/thumbnail.png"),
        },
    )

The ``videogif`` argument is now the ``"gif"`` key of the ``video`` dict:

Old:

.. code-block:: python
    :class: code-old

    reddit.subreddit("test").submit_video("My Title", "/path/to/video.mp4", videogif=True)

New:

.. code-block:: python

    from praw.models import PostMedia

    reddit.subreddit("test").submit(
        "My Title", video={"gif": True, "media": PostMedia("/path/to/video.mp4")}
    )

Submitting a gallery
====================

Gallery items are either a bare :class:`.PostMedia`, or a ``dict`` with a ``media`` key
(replacing ``image_path``) when a ``caption`` or ``outbound_url`` is desired.

Old:

.. code-block:: python
    :class: code-old

    images = [
        {"image_path": "/path/to/image.png"},
        {"image_path": "/path/to/image2.png", "caption": "a caption"},
    ]
    reddit.subreddit("test").submit_gallery("My Title", images)

New:

.. code-block:: python

    from praw.models import PostMedia

    gallery = [
        PostMedia("/path/to/image.png"),
        {"caption": "a caption", "media": PostMedia("/path/to/image2.png")},
    ]
    reddit.subreddit("test").submit("My Title", gallery=gallery)

Submitting a poll
=================

The ``options`` and ``duration`` arguments are now keys of the ``poll`` dict.
``selftext`` is no longer required for polls.

Old:

.. code-block:: python
    :class: code-old

    reddit.subreddit("test").submit_poll(
        "Do you like PRAW?", duration=3, options=["Yes", "No"], selftext=""
    )

New:

.. code-block:: python

    reddit.subreddit("test").submit(
        "Do you like PRAW?", poll={"duration": 3, "options": ["Yes", "No"]}
    )

*********************************
 ``user.me()`` in read-only mode
*********************************

Calling ``reddit.user.me()`` in :attr:`.read_only` mode previously returned ``None``
with a deprecation warning. It now raises :class:`.ReadOnlyException`.

Old:

.. code-block:: python
    :class: code-old

    if reddit.user.me() is None:
        print("Not authenticated")

New:

.. code-block:: python

    from praw.exceptions import ReadOnlyException

    try:
        reddit.user.me()
    except ReadOnlyException:
        print("Not authenticated")

***********************************************
 ``Redditor.subreddit`` is a ``UserSubreddit``
***********************************************

The ``subreddit`` attribute of :class:`.Redditor` is a :class:`.UserSubreddit` instance.
Its values are accessed as attributes; the ``dict`` interface has been removed.

Old:

.. code-block:: python
    :class: code-old

    title = redditor.subreddit["title"]

New:

.. code-block:: python

    title = redditor.subreddit.title

*********************************
 Link submissions with body text
*********************************

The ``selftext`` and ``url`` arguments to :meth:`.Subreddit.submit` are no longer
mutually exclusive. When ``url`` is provided, ``selftext`` is used as optional
Markdown-formatted body text to accompany the link submission. The same applies to
``gallery``, ``image``, ``poll``, and ``video`` submissions.

One exception: combining ``inline_media`` with ``selftext`` for a ``url`` submission
raises an exception, because Reddit does not support inline media in body text for link
submissions.

******************************************
 Arguments that must be passed by keyword
******************************************

The following arguments must now be passed by keyword:

- The ``mark_read`` argument when calling ``subreddit.modmail`` to fetch a
  :class:`.ModmailConversation`, e.g., ``reddit.subreddit("test").modmail("2gmz",
  mark_read=True)``.
- The ``is_link`` argument to :meth:`.SubredditFlairTemplates.flair_type`.
- The ``data`` argument to ``Objector.objectify``.

*********
 Renamed
*********

- The ``reason_id`` argument to :class:`.RemovalReason` has been renamed to ``id``.
- ``APIException`` has been removed; use :class:`.RedditAPIException`. See the `PRAW 7
  migration documentation
  <https://praw.readthedocs.io/en/v7.8.2/package_info/praw7_migration.html>`_ for
  details on the exception container interface.
- ``Subreddits.gold`` has been removed; use :meth:`.Subreddits.premium`.

*************
 Old modmail
*************

Reddit retired the old modmail system, so ``Subreddit.mod.inbox``,
``Subreddit.mod.unread``, ``Subreddit.mod.stream.unread``, ``SubredditMessage.mute``,
and ``SubredditMessage.unmute`` have been removed. Use the new modmail interface
instead.

Old:

.. code-block:: python
    :class: code-old

    for message in reddit.subreddit("test").mod.unread():
        print(message.subject)

New:

.. code-block:: python

    for conversation in reddit.subreddit("test").modmail.conversations(state="new"):
        print(conversation.subject)

To stream conversations, use :meth:`.SubredditModerationStream.modmail_conversations`
(``subreddit.mod.stream.modmail_conversations()``). Muting and unmuting users is
available on :class:`.ModmailConversation` via :meth:`.ModmailConversation.mute` and
:meth:`.ModmailConversation.unmute`.

The ``after`` argument for :meth:`.conversations` has also been removed. To resume a
listing from a known conversation, pass ``after`` through ``params``:

.. code-block:: python

    conversations = reddit.subreddit("test").modmail.conversations(params={"after": "2gmz"})

****************
 Token managers
****************

The ``token_manager`` keyword argument to :class:`.Reddit`, along with
``BaseTokenManager``, ``FileTokenManager``, and ``SQLiteTokenManager``, has been
removed. Refresh tokens no longer rotate, so a static ``refresh_token`` can be provided
directly.

Old:

.. code-block:: python
    :class: code-old

    from praw.util.token_manager import FileTokenManager

    reddit = praw.Reddit(..., token_manager=FileTokenManager("token.txt"))

New:

.. code-block:: python

    reddit = praw.Reddit(..., refresh_token="...")

See :ref:`refresh_token` for the complete guide to obtaining and using refresh tokens.

*********************************
 Subreddit Module Reorganization
*********************************

The single ``praw/models/reddit/subreddit.py`` file has been split into a
``praw.models.reddit.subreddit`` package. The :class:`.Subreddit` class and each of its
helper classes now live in their own module:

.. list-table::
    :header-rows: 1
    :widths: 50 50

    - - Class
      - New module
    - - :class:`.Subreddit`
      - ``praw.models.reddit.subreddit.subreddit``
    - - :class:`.Modmail`
      - ``praw.models.reddit.subreddit.modmail``
    - - :class:`.SubredditFilters`
      - ``praw.models.reddit.subreddit.filters``
    - - :class:`.SubredditFlair`, :class:`.SubredditFlairTemplates`,
        :class:`.SubredditLinkFlairTemplates`, :class:`.SubredditRedditorFlairTemplates`
      - ``praw.models.reddit.subreddit.flair``
    - - :class:`.SubredditModeration`, :class:`.SubredditModerationStream`
      - ``praw.models.reddit.subreddit.moderation``
    - - :class:`.SubredditQuarantine`
      - ``praw.models.reddit.subreddit.quarantine``
    - - :class:`.SubredditRelationship`, :class:`.ContributorRelationship`,
        :class:`.ModeratorRelationship`
      - ``praw.models.reddit.subreddit.relationship``
    - - :class:`.SubredditStream`
      - ``praw.models.reddit.subreddit.stream``
    - - :class:`.SubredditStylesheet`
      - ``praw.models.reddit.subreddit.stylesheet``
    - - :class:`.SubredditWiki`
      - ``praw.models.reddit.subreddit.wiki``

All of these classes remain importable from ``praw.models.reddit.subreddit`` and
``praw.models`` for backwards compatibility, so existing imports of the form ``from
praw.models.reddit.subreddit import Subreddit`` continue to work unchanged. Update
direct imports only if you were depending on the module file's location on disk (for
example, in tooling or monkeypatches).

*****************************
 Removed without replacement
*****************************

The following were removed because Reddit no longer supports the underlying endpoints or
features:

- ``Reddit.random_subreddit``, ``Subreddit.random``, and ``Subreddit.random_rising`` —
  Reddit removed the random subreddit and random submission endpoints.
- ``Comment.award``, ``Submission.award``, and the ``gild`` aliases on
  :class:`.Comment`, :class:`.Redditor`, and :class:`.Submission` — Reddit removed the
  awards API.
- ``Redditor.gilded``, ``Subreddit.gilded``, and ``Redditor.gildings`` — gilded listings
  were removed along with the awards API.
- ``Subreddits.search_by_topic`` — the endpoint has returned 404 since 2020.
- ``Reddit.validate_on_submit`` — Reddit now always validates posts on submission, so
  the setting no longer has any effect. Remove any assignments to it.
- ``WebSocketException.original_exception``.
- ``InboxableMixin.unblock_subreddit``.
- The ``reset_timestamp`` key in the dictionary returned by :meth:`.limits` — the
  remaining keys are ``remaining`` and ``used``.
