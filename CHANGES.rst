Change Log
==========

Unreleased
----------

0.dev0 (2021/02/08)
-------------------

**Added**

* Add method :meth:`~.Subreddits.premium` to reflect the naming change in Reddit's API.
* Ability to submit image galleries with :meth:`.submit_gallery`.
* Ability to pass a gallery url to :meth:`.Reddit.submission`.
* Ability to specify modmail mute duration.
* Add method :meth:`.invited` to get invited moderators of a subreddit.
* Ability to submit text/self posts with inline media.
* Add method :meth:`~.Submission.award` and :meth:`~.Comment.award` with the ability to
  specify type of award, anonymity, and message when awarding a submission or comment.
* Ability to specify subreddits by name using the `subreddits` parameter in
  :meth:`.Reddit.info`.
* A check to see if PRAW is running in an asynchronous environment and will advise the
  user to use `Async PRAW <https://asyncpraw.readthedocs.io>`_. This also adds a
  configuration option to disable the check.

**Changed**

* Drop support for Python 3.5, which is end-of-life on 2020-09-13.
* :class:`~.BoundedSet` will now utilize a Last-Recently-Used (LRU) storing mechanism,
  which will change the order in which elements are removed from the set.
* Improved :meth:`.submit_image` and :meth:`.submit_video` performance in slow
  network environments by removing a race condition when establishing a
  websocket connection.

**Deprecated**

* :meth:`~.Subreddits.gold` is superseded by :meth:`~.Subreddits.premium`.
* :meth:`~.Submission.gild` is superseded by :meth:`~.Submission.award`.
* :meth:`~.Comment.gild` is superseded by :meth:`~.Comment.award`.

**Fixed**

* An issue where leaving as a moderator fails if you are using token auth.
* An issue where an incorrect error was being raised due to invalid submission urls.
* Some cases where streams yield the same item multiple times. This cannot be
  prevented in every case.


7.1.4 (2021/02/07)
------------------

**Fixed**

* Asynchronous check will no longer fail in Python 3.6 multithreading edge cases.

7.1.3 (2021/02/05)
------------------

**Changed**

* Asynchronous check will no longer occur when in a Jupyter notebook.

7.1.2 (2021/02/03)
------------------

**Fixed**

* Asynchronous check would not work on Python 3.6 as ``asyncio.get_running_loop`` only
  exists on Python 3.7+.

7.1.1 (2021/02/02)
------------------

**Added**

* Add method :meth:`~.Subreddits.premium` to reflect the naming change in Reddit's API.
* Ability to submit image galleries with :meth:`.submit_gallery`.
* Ability to pass a gallery url to :meth:`.Reddit.submission`.
* Ability to specify modmail mute duration.
* Add method :meth:`.invited` to get invited moderators of a subreddit.
* Ability to submit text/self posts with inline media.
* Add method :meth:`~.Submission.award` and :meth:`~.Comment.award` with the ability to
  specify type of award, anonymity, and message when awarding a submission or comment.
* Ability to specify subreddits by name using the `subreddits` parameter in
  :meth:`.Reddit.info`.
* A check to see if PRAW is running in an asynchronous environment and will advise the
  user to use `Async PRAW <https://asyncpraw.readthedocs.io>`_. This also adds a
  configuration option to disable the check.

**Changed**

* Drop support for Python 3.5, which is end-of-life on 2020-09-13.
* :class:`~.BoundedSet` will now utilize a Last-Recently-Used (LRU) storing mechanism,
  which will change the order in which elements are removed from the set.
* Improved :meth:`.submit_image` and :meth:`.submit_video` performance in slow
  network environments by removing a race condition when establishing a
  websocket connection.

**Deprecated**

* :meth:`~.Subreddits.gold` is superseded by :meth:`~.Subreddits.premium`.
* :meth:`~.Submission.gild` is superseded by :meth:`~.Submission.award`.
* :meth:`~.Comment.gild` is superseded by :meth:`~.Comment.award`.

**Fixed**

* An issue where leaving as a moderator fails if you are using token auth.
* An issue where an incorrect error was being raised due to invalid submission urls.
* Some cases where streams yield the same item multiple times. This cannot be
  prevented in every case.

7.1.0 (2020/06/22)
------------------

**Added**

* :class:`.Rule` to represent one rule of a subreddit.
* :class:`.SubredditRules` to get and add rules.
* Ability to submit polls with :meth:`.submit_poll`.
* :class:`.PollData` and :class:`.PollOption`.
* Ability to view poll data and poll options via the ``.poll_data`` attribute on poll
  submissions.
* Add method :meth:`~.Reddit.delete` to :class:`.Reddit` class to support HTTP DELETE
  requests.
* Added :class:`.CalendarConfiguration` to represent the configuration of a
  :class:`.Calendar` widget.
* Added :class:`.Hover` to represent the hover state of a :class:`.Button`.
* Added :class:`.Styles` to represent widget styling information.
* Ability to stream live thread updates via new class :class:`.LiveThreadStream` with
  method :meth:`~.LiveThreadStream.updates`.

**Changed**

* :meth:`.RemovalReason.update`\ 's parameters are now optional.
* :meth:`.SubredditRemovalReasons.__getitem__` now takes integers and slices to get
  removal reasons from the list of reasons as returned by Reddit.

**Deprecated**

* :attr:`.WebSocketException.original_exception` is deprecated and slated for removal in
  PRAW 8.0.

**Fixed**

* An issue where certain subreddit settings could not be set through
  :meth:`.SubredditModeration.update`, such as ``welcome_message_enabled`` and
  ``welcome_message_text``. This change also removes the need for PRAW to track current
  subreddit settings and send unmodified ones in the update request.
* Instances of ``BadRequest``\ s captured by PRAW that do not contain any detailed JSON
  data are re-raised as the original ``BadRequest``.
* :meth:`.submit_image` and :meth:`.submit_video` will throw :class:`.MediaPostFailed`
  when Reddit fails to post an image or video post.


7.0.0 (2020/04/24)
------------------

**Added**

* ``config_interpolation`` parameter for :class:`.Reddit` supporting basic and extended
  modes.
* Add :meth:`.Redditors.partial_redditors` that returns lightweight redditor objects
  that contain only a few fields. This is useful for resolving Redditor IDs to their
  usernames in bulk.
* :meth:`.User.friends` has a new parameter ``user`` that takes either an instance of
  :class:`.Redditor` or a string containing a redditor name and returns an instance of
  :class:`.Redditor` if the authenticated user is friends with the user, otherwise
  throws an exception.
* :meth:`.SubmissionModeration.flair` has the parameter ``flair_template_id`` for
  applying flairs with template IDs.
* :meth:`~.Emoji.update` supports modifying an emoji's permissions.
* :meth:`~.SubredditEmoji.add` now supports optionally passing booleans to set an
  emoji's permissions upon upload.
* Methods :meth:`.SubredditLinkFlairTemplates.update` and
  :meth:`.SubredditRedditorFlairTemplates.update` contain a new parameter, ``fetch``,
  that toggles the automatic fetching of existing data from Reddit. It is set to True by
  default.
* Values in methods :meth:`.SubredditLinkFlairTemplates.update` and
  :meth:`.SubredditRedditorFlairTemplates.update` that are left as the defaults will no
  longer be over-written if the ``fetch`` parameter is set to ``True``, but will fill in
  existing values for the flair template.
* The parameter ``text`` for methods :meth:`.SubredditLinkFlairTemplates.update` and
  :meth:`.SubredditRedditorFlairTemplates.update` is no longer required.
* There is a new method, :meth:`.Subreddit.post_requirements`, to fetch a subreddit's
  post requirements.
* Method :meth:`.SubmissionModeration.sticky` will now ignore the Conflict exception
  generated by trying to sticky the same post multiple times.
* A new method :meth:`.CommentModeration.show` will uncollapse a comment that was
  collapsed because of Crowd Control
* Methods :meth:`.Subreddit.submit_image` and :meth:`.Subreddit.submit_video` will throw
  :class:`.TooLargeMediaException` if the submitted media is rejected by Reddit due to
  the size of the media.
* Class :class:`.Reddit` has an attribute, ``validate_on_submit``, that can be set after
  class initialization that causes methods :meth:`.Subreddit.submit`,
  :meth:`.Subreddit.submit_image`, :meth:`.Subreddit.submit_video`, and
  :meth:`.Submission.edit` to check that the submission matches a subreddit's post
  validation rules. This attribute will be functionally useless once Reddit implements
  their change. This attribute will be deprecated on the next release after Reddit's
  change, and will be removed on the next major release after Reddit's change.

.. warning::

    In May-June 2020, Reddit will force all submissions to run through a subreddit's
    validation rules.

* Introduced a data class, :class:`.RedditErrorItem`, to represent an individual error
  item returned from Reddit.
* Class :class:`.RedditAPIException` now serves as a container for the
  :class:`.RedditErrorItem`\ s. You can access the items by doing
  ``RedditAPIException.items``, which returns a list.
* :class:`.APIException` is an alias to :class:`.RedditAPIException`.
* Parameter ``discussion_type`` to methods :meth:`.Subreddit.submit`,
  :meth:`.Subreddit.submit_image`, and :meth:`.Subreddit.submit_video` to support
  submitting as a live discussion (set to ``CHAT``).
* Instances of :class:`.Trophy` can be compared for equality with each other.
* :class:`.Reddit` has a new configurable parameter, ``timeout``. This defaults to 16
  seconds. It controls how long PRAW will wait for a response before throwing an
  exception.
* PRAW now handles ratelimit errors returned as instances of
  :class:`.RedditAPIException`.
* :class:`.Reddit` has one new parameter, ``ratelimit_seconds`` . The parameter
  configures the maximum amount of seconds to catch ratelimits for. It defaults to 5
  seconds when not specified.

**Changed**

* ``prawcore.BadRequest`` should no longer be raised. Instead a more useful
  :class:`.RedditAPIException` instance will be raised.
* Set the default comment sort to ``confidence`` instead of ``best`` because it turns
  out ``best`` isn't actually the correct value for the parameter.

**Deprecated**

* :class:`.APIException` is deprecated and slated for removal in PRAW 8.0.

**Fixed**

* :meth:`.SubredditFlair.update` will not error out when the flair text contains quote
  marks.

**Removed**

* Converting :class:`.APIException` to string will no longer escape unicode characters.
* Module ``praw.models.modaction`` no longer exists. Please use the module
  ``praw.models.mod_action``, or directly import ``ModAction`` from ``praw.models``.
* Methods :meth:`.SubredditLinkFlairTemplates.update` and
  :meth:`.SubredditRedditorFlairTemplates.update` will no longer create flairs that are
  using an invalid template id, but instead throw a :class:`.InvalidFlairTemplateID`.
* Method ``reddit.user.moderator_subreddits`` has been removed. Please use
  :meth:`.Redditor.moderated` instead.

6.5.1 (2020/01/07)
------------------

**Fixed**

* Removed usages of ``NoReturn`` that caused PRAW to fail due to ``ImportError`` in
  Python ``<3.5.4`` and ``<3.6.2``.

6.5.0 (2020/01/05)
------------------

**Added**

* :meth:`.set_original_content` supports marking a submission as original content.
* :meth:`.unset_original_content` supports unmarking a submission as original content.
* :meth:`.Redditor.moderated` to get a list of a Redditor's moderated subreddits.
* Parameter ``without_websockets`` to :meth:`~.Subreddit.submit_image` and
  :meth:`~.Subreddit.submit_video` to submit without using WebSockets.
* :meth:`.Reddit.redditor` supports ``fullname`` param to fetch a Redditor by the
  fullname instead of name. :class:`.Redditor` constructor now also has ``fullname``
  param.
* Add :class:`.RemovalReason` and :class:`.SubredditRemovalReasons` to work with removal
  reasons
* Attribute ``removal_reasons`` to :class:`.SubredditModeration` to interact with new
  removal reason classes
* Parameters ``mod_note`` and ``reason_id`` to :meth:`.ThingModerationMixin.remove` to
  optionally apply a removal reason on removal
* Add :class:`.SubredditModerationStream` to enable moderation streams
* Attribute ``stream`` to :class:`.SubredditModeration` to interact with new moderation
  streams
* Add :meth:`.SubredditModerationStream.edited` to allow streaming of
  :meth:`.SubredditModeration.edited`
* Add :meth:`.SubredditModerationStream.log` to allow streaming of
  :meth:`.SubredditModeration.log`
* Add :meth:`.SubredditModerationStream.modmail_conversations` to allow streaming of
  :meth:`.Modmail.conversations`
* Add :meth:`.SubredditModerationStream.modqueue` to allow streaming of
  :meth:`.SubredditModeration.modqueue`
* Add :meth:`.SubredditModerationStream.reports` to allow streaming of
  :meth:`.SubredditModeration.reports`
* Add :meth:`.SubredditModerationStream.spam` to allow streaming of
  :meth:`.SubredditModeration.spam`
* Add :meth:`.SubredditModerationStream.unmoderated` to allow streaming of
  :meth:`.SubredditModeration.unmoderated`
* Add :meth:`.SubredditModerationStream.unread` to allow streaming of
  :meth:`.SubredditModeration.unread`
* Parameter ``exclude_before`` to :func:`.stream_generator` to allow
  :meth:`.SubredditModerationStream.modmail_conversations` to work
* Parameters ``allowable_content`` and ``max_emojis`` to
  :meth:`~.SubredditRedditorFlairTemplates.add`,
  :meth:`~.SubredditLinkFlairTemplates.add`, and
  :meth:`~.SubredditFlairTemplates.update`, as well as its child classes.

**Deprecated**

* Method ``reddit.user.moderator_subreddits`` as :meth:`.Redditor.moderated` provides
  more functionality.
* The file for ModActions (praw/models/modaction.py) has been moved to
  praw/models/mod_action.py and the previous has been Deprecated.

**Expected Changes**

* The behavior of ``APIException`` will no longer unicode-escape strings in the next
  minor release.

6.4.0 (2019/09/21)
------------------

**Added**

* :meth:`~.Submission.crosspost` support parameter ``flair_id`` to flair the submission
  immediately upon crossposting.
* :meth:`~.Submission.crosspost` support parameter ``flair_text`` to set a custom text
  to the flair immediately upon crossposting.
* :meth:`~.Submission.crosspost` support parameter ``nsfw`` to mark the submission NSFW
  immediately upon crossposting.
* :meth:`~.Submission.crosspost` support parameter ``spoiler`` to mark the submission as
  a spoiler immediately upon crossposting.

**Fixed**

* :meth:`.add_community_list` has parameter ``description`` to support unannounced
  upstream Reddit API changes.
* :meth:`~.WidgetModeration.update` supports passing a list of :class:`.Subreddit`
  objects.

**Changed**

* Removed ``css_class`` parameter cannot be used with ``background_color``,
  ``text_color``, or ``mod_only`` constraint on methods:

  * ``SubredditFlairTemplates.update()``
  * ``SubredditRedditorFlairTemplates.add()``
  * ``SubredditLinkFlairTemplates.add()``

**Removed**

* Drop official support for Python 2.7.
* ``Multireddit.rename()`` no longer works due to a change in the Reddit API.

6.3.1 (2019/06/10)
------------------

**Removed**

* ``SubredditListingMixin.gilded()``, as this was supposed to be removed in 6.0.0 after
  deprecation in 5.2.0.

6.3.0 (2019/06/09)
------------------

**Added**

* Collections (:class:`.Collection` and helper classes).
* :meth:`.submit`, :meth:`.submit_image`, and :meth:`.submit_video` can be used to
  submit a post directly to a collection.
* ``praw.util.camel_to_snake`` and ``praw.util.snake_case_keys``.
* Comments can now be locked and unlocked via ``comment.mod.lock()`` and
  ``comment.mod.unlock()``. See: (:meth:`.ThingModerationMixin.lock` and
  :meth:`.ThingModerationMixin.unlock`).
* ``align`` parameter to :meth:`.SubredditStylesheet.upload_banner_additional_image`

**Changed**

* :meth:`.Reddit.info` now accepts any non-str iterable for fullnames (not just
  ``list``).
* :meth:`.Reddit.info` now returns a generator instead of a list when using the ``url``
  parameter.

6.2.0 (2019/05/05)
------------------

**Added**

* :meth:`.SubredditStylesheet.upload_banner`
* :meth:`.SubredditStylesheet.upload_banner_additional_image`
* :meth:`.SubredditStylesheet.upload_banner_hover_image`
* :meth:`.SubredditStylesheet.delete_banner`
* :meth:`.SubredditStylesheet.delete_banner_additional_image`
* :meth:`.SubredditStylesheet.delete_banner_hover_image`
* :meth:`~.Subreddit.submit`, :meth:`~.Subreddit.submit_image`, and
  :meth:`~.Subreddit.submit_video` support parameter ``nsfw`` to mark the submission
  NSFW immediately upon posting.
* :meth:`~.Subreddit.submit`, :meth:`~.Subreddit.submit_image`, and
  :meth:`~.Subreddit.submit_video` support parameter ``spoiler`` to mark the submission
  as a spoiler immediately upon posting.
* :meth:`~.Subreddit.submit_image` and :meth:`~.Subreddit.submit_video` support
  parameter ``timeout``. Default timeout has been raised from 2 seconds to 10 seconds.
* Added parameter ``function_kwargs`` to :func:`.stream_generator` to pass additional
  kwargs to ``function``.

**Fixed**

* :meth:`.Subreddit.random` returns ``None`` instead of raising
  :class:`.ClientException` when the subreddit does not support generating random
  submissions.

**Other**

* Bumped minimum prawcore version to 1.0.1.

6.1.1 (2019/01/29)
------------------

**Added**

* :meth:`~.SubredditFlair.set` supports parameter ``flair_template_id`` for giving a
  user redesign flair.

6.1.0 (2019/01/19)
------------------

**Added**

* Add method :meth:`.Redditor.trophies` to get a list of the Redditor's trophies.
* Add class :class:`.PostFlairWidget`.
* Add attributes ``reply_limit`` and ``reply_sort`` to class :class:`.Comment`
* Add class :class:`.SubredditWidgetsModeration` (accessible through
  :attr:`.SubredditWidgets.mod`) and method :meth:`.add_text_area`.
* Add class :class:`.WidgetModeration` (accessible through the ``.mod`` attribute on any
  widget) with methods :meth:`~.WidgetModeration.update` and
  :meth:`~.WidgetModeration.delete`.
* Add method :meth:`.Reddit.put` for HTTP PUT requests.
* Add methods :meth:`.add_calendar` and :meth:`.add_community_list`.
* Add methods :meth:`.add_image_widget` and :meth:`.upload_image`.
* Add method :meth:`.add_custom_widget`.
* Add method :meth:`.add_post_flair_widget`.
* Add method :meth:`.add_menu`.
* Add method :meth:`.add_button_widget`.
* Add method :meth:`~.SubredditWidgetsModeration.reorder` to reorder a subreddit's
  widgets.
* Add :class:`.Redditors` (``reddit.redditors``) to provide Redditor listings.
* Add :meth:`.submit_image` for submitting native images to Reddit.
* Add :meth:`.submit_video` for submitting native videos and videogifs to Reddit.

**Changed**

* :meth:`.User.me` returns ``None`` in :attr:`~praw.Reddit.read_only` mode.
* :meth:`.SubredditLinkFlairTemplates.__iter__` uses the v2 flair API endpoint. This
  change will result in additional fields being returned. All fields that were
  previously returned will still be returned.
* :meth:`.SubredditRedditorFlairTemplates.__iter__` uses the v2 flair API endpoint. The
  method will still return the exact same items.
* Methods :meth:`~.SubredditRedditorFlairTemplates.add`,
  :meth:`~.SubredditLinkFlairTemplates.add`,
  :meth:`~.SubredditRedditorFlairTemplates.update`, and
  :meth:`~.SubredditLinkFlairTemplates.update` can add and update redesign-style flairs
  with the v2 flair API endpoint. They can still update pre-redesign-style flairs with
  the older endpoint.

**Fixed**

* Widgets of unknown types are parsed as ``Widget``\ s rather than raising an exception.

6.0.0 (2018/07/24)
------------------

**Added**

* Add method :meth:`.WikiPage.revision` to get a specific wiki page revision.
* Added parameter ``skip_existing`` to :func:`.stream_generator` to skip existing items
  when starting a stream.
* Add method :meth:`.Front.best` to get the front page "best" listing.
* Add :attr:`.Subreddit.widgets`, :class:`.SubredditWidgets`, and widget subclasses like
  :class:`.TextArea` to support fetching Reddit widgets.
* Add method :meth:`.Submission.mark_visited` to mark a submission as visited on the
  Reddit backend.

**Fixed**

* Fix ``RecursionError`` on :class:`.SubredditEmoji`'s ``repr`` and ``str``.
* :meth:`.SubredditFilters.add` and :meth:`.SubredditFilters.remove`
  also accept a :class:`.Subreddit` for the ``subreddit`` parameter.
* Remove restriction which prevents installed (non-confidential) apps from
  using OAuth2 authorization code grant flow.

**Removed**

* ``Subreddit.submissions`` as the API endpoint backing the method is no more. See
  https://www.reddit.com/r/changelog/comments/7tus5f/update_to_search_api/.

5.4.0 (2018/03/27)
------------------

**Added**

* Add method :meth:`~.Reddit.patch` to :class:`.Reddit` class to support HTTP PATCH
  requests.
* Add class :class:`.Preferences` to access and update Reddit preferences.
* Add attribute :attr:`.User.preferences` to access an instance of
  :class:`.Preferences`.
* Add method :meth:`.Message.delete()`.
* Add class :class:`.Emoji` to work with custom subreddit emoji.

**Deprecated**

* ``Subreddit.submissions`` as the API endpoint backing the method is going away. See
  https://www.reddit.com/r/changelog/comments/7tus5f/update_to_search_api/.


**Fixed**

* Fix bug with positive ``pause_after`` values in streams provided by
  :func:`.stream_generator` where the wait time was not reset after a yielded ``None``.
* Parse URLs with trailing slashes and no ``"comments"`` element when creating
  :class:`.Submission` objects.
* Fix bug where ``Subreddit.submissions`` returns a same submission more than once
* Fix bug where ``ListingGenerator`` fetches the same batch of submissions in an
  infinite loop when ``"before"`` parameter is provided.

**Removed**

* Removed support for Python 3.3 as it is no longer supported by requests.


5.3.0 (2017/12/16)
------------------

**Added**

* :attr:`.Multireddit.stream`, to stream submissions and comments from a Multireddit.
* :meth:`.Redditor.block`

**Fixed**

* Now raises ``prawcore.UnavailableForLegalReasons`` instead of an ``AssertionError``
  when encountering a HTTP 451 response.


5.2.0 (2017/10/24)
------------------

**Changed**

* An attribute on :class:`.LiveUpdate` now works as lazy attribute (i.e. populate an
  attribute when the attribute is first accessed).

**Deprecated**

* ``subreddit.comments.gilded`` because there isn't actually an endpoint that returns
  only gilded comments. Use ``subreddit.gilded`` instead.

**Fixed**

* Removed ``comment.permalink()`` because ``comment.permalink`` is now an attribute
  returned by Reddit.


5.1.0 (2017/08/31)
------------------

**Added**

* :attr:`.Redditor.stream`, with methods :meth:`.RedditorStream.submissions()` and
  :meth:`.RedditorStream.comments()` to stream a Redditor's comments or submissions
* :class:`.RedditorStream` has been added to facilitate :attr:`.Redditor.stream`
* :meth:`.Inbox.collapse` to mark messages as collapsed.
* :meth:`.Inbox.uncollapse` to mark messages as uncollapsed.
* Raise :class:`.ClientException` when calling :meth:`~.Comment.refresh` when the
  comment does not appear in the resulting comment tree.
* :meth:`.Submission.crosspost` to crosspost to a subreddit.

**Fixed**

* Calling :meth:`~.Comment.refresh` on a directly fetched, deeply nested
  :class:`.Comment` will additionally pull in as many parent comments as possible
  (currently 8) enabling significantly quicker traversal to the top-most
  :class:`.Comment` via successive :meth:`.parent()` calls.
* Calling :meth:`~.Comment.refresh` previously could have resulted in a
  ``AttributeError: "MoreComments" object has no attribute "_replies"`` exception. This
  situation will now result in a :class:`.ClientException`.
* Properly handle ``BAD_CSS_NAME`` errors when uploading stylesheet images with invalid
  filenames. Previously an ``AssertionError`` was raised.
* :class:`.Submission`'s ``gilded`` attribute properly returns the expected value from
  reddit.


5.0.1 (2017/07/11)
------------------

**Fixed**

* Calls to :meth:`.hide()` and :meth:`.unhide()` properly batch into requests of 50
  submissions at a time.
* Lowered the average maximum delay between inactive stream checks by 4x to 16 seconds.
  It was previously 64 seconds, which was too long.

5.0.0 (2017/07/04)
------------------

**Added**

* :meth:`.Comment.disable_inbox_replies`, :meth:`.Comment.enable_inbox_replies`
  :meth:`.Submission.disable_inbox_replies`, and
  :meth:`.Submission.enable_inbox_replies` to toggle inbox replies on comments and
  submissions.

**Changed**

* ``cloudsearch`` is no longer the default syntax for :meth:`.Subreddit.search`.
  ``lucene`` is now the default syntax so that PRAW's default is aligned with Reddit's
  default.
* :meth:`.Reddit.info` will now take either a list of fullnames or a single URL string.
* :meth:`.Subreddit.submit` accepts a flair template ID and text.

**Fixed**

* Fix accessing :attr:`.LiveUpdate.contrib` raises ``AttributeError``.

**Removed**

* Iterating directly over :class:`.SubredditRelationship` (e.g., ``subreddit.banned``,
  ``subreddit.contributor``, ``subreddit.moderator``, etc) and :class:`.SubredditFlair`
  is no longer possible. Iterate instead over their callables, e.g.
  ``subreddit.banned()`` and ``subreddit.flair()``.
* The following methods are removed: ``Subreddit.mod.approve``,
  ``Subreddit.mod.distinguish``, ``Subreddit.mod.ignore_reports``,
  ``Subreddit.mod.remove``, ``Subreddit.mod.undistinguish``,
  ``Subreddit.mod.unignore_reports``.
* Support for passing a :class:`.Submission` to :meth:`.SubredditFlair.set` is removed.
* The ``thing`` argument to :meth:`.SubredditFlair.set` is removed.
* Return values from :meth:`.Comment.block`, :meth:`.Message.block`,
  :meth:`.SubredditMessage.block`, :meth:`.SubredditFlair.delete`, :meth:`.friend`,
  :meth:`.Redditor.message`, :meth:`.Subreddit.message`, :meth:`.select`, and
  :meth:`.unfriend` are removed as they do not provide any useful information.
* ``praw.ini`` no longer reads in ``http_proxy`` and ``https_proxy`` settings.
* ``is_link`` parameter of :meth:`.SubredditRedditorFlairTemplates.add` and
  :meth:`.SubredditRedditorFlairTemplates.clear`. Use
  :class:`.SubredditLinkFlairTemplates` instead.

4.6.0 (2017/07/04)
------------------

The release's sole purpose is to announce the deprecation of the ``is_link`` parameter
as described below:

**Added**

* :attr:`.SubredditFlair.link_templates` to manage link flair templates.

**Deprecated**

* ``is_link`` parameter of :meth:`.SubredditRedditorFlairTemplates.add` and
  :meth:`.SubredditRedditorFlairTemplates.clear`. Use
  :class:`.SubredditLinkFlairTemplates` instead.

4.5.1 (2017/05/07)
------------------

**Fixed**

* Calling :meth:`.parent` works on :class:`.Comment` instances obtained via
  :meth:`.comment_replies`.


4.5.0 (2017/04/29)
------------------

**Added**

* :meth:`~praw.models.reddit.subreddit.Modmail.unread_count` to get unread count by
  conversation state.
* :meth:`~praw.models.reddit.subreddit.Modmail.bulk_read` to mark conversations as read
  by conversation state.
* :meth:`~praw.models.reddit.subreddit.Modmail.subreddits` to fetch subreddits using new
  modmail.
* :meth:`~praw.models.reddit.subreddit.Modmail.create` to create a new modmail
  conversation.
* :meth:`~praw.models.ModmailConversation.read` to mark modmail conversations as read.
* :meth:`~praw.models.ModmailConversation.unread` to mark modmail conversations as
  unread.
* :meth:`~praw.models.reddit.subreddit.Modmail.conversations` to get new modmail
  conversations.
* :meth:`~praw.models.ModmailConversation.highlight` to highlight modmail conversations.
* :meth:`~praw.models.ModmailConversation.unhighlight` to unhighlight modmail
  conversations.
* :meth:`~praw.models.ModmailConversation.mute` to mute modmail conversations.
* :meth:`~praw.models.ModmailConversation.unmute` to unmute modmail conversations.
* :meth:`~praw.models.ModmailConversation.archive` to archive modmail conversations.
* :meth:`~praw.models.ModmailConversation.unarchive` to unarchive modmail conversations.
* :meth:`~praw.models.ModmailConversation.reply` to reply to modmail conversations.
* :meth:`~praw.models.reddit.subreddit.Modmail.__call__` to get a new modmail
  conversation.
* :meth:`.Inbox.stream` to stream new items in the inbox.
* Exponential request delay to all streams when no new items are returned in a request.
  The maximum delay between requests is 66 seconds.

**Changed**

* :meth:`.submit` accepts ``selftext=''`` to create a title-only submission.
* :class:`.Reddit` accepts ``requestor_class=cls`` for a customized requestor class and
  ``requestor_kwargs={"param": value}`` for passing arguments to requestor
  initialization.
* :meth:`~praw.models.reddit.subreddit.SubredditStream.comments`,
  :meth:`~praw.models.reddit.subreddit.SubredditStream.submissions`, and
  :meth:`~praw.models.Subreddits.stream` accept a ``pause_after`` argument to allow
  pausing of the stream. The default value of ``None`` retains the preexisting behavior.

**Deprecated**

* ``cloudsearch`` will no longer be the default syntax for :meth:`.Subreddit.search` in
  PRAW 5. Instead ``lucene`` will be the default syntax so that PRAW's default is
  aligned with Reddit's default.

**Fixed**

* Fix bug where :class:`.WikiPage` revisions with deleted authors caused ``TypeError``.
* :class:`.Submission` attributes ``comment_limit`` and ``comment_sort`` maintain their
  values after making instances non-lazy.

4.4.0 (2017/02/21)
------------------

**Added**

* :meth:`.LiveThreadContribution.update` to update settings of a live thread.
* ``reset_timestamp`` to :meth:`.limits` to provide insight into when the current rate
  limit window will expire.
* :meth:`.upload_mobile_header` to upload subreddit mobile header.
* :meth:`.upload_mobile_icon` to upload subreddit mobile icon.
* :meth:`.delete_mobile_header` to remove subreddit mobile header.
* :meth:`.delete_mobile_icon` to remove subreddit mobile icon.
* :meth:`.LiveUpdateContribution.strike` to strike a content of a live thread.
* :meth:`.LiveContributorRelationship.update` to update contributor permissions for a
  redditor.
* :meth:`.LiveContributorRelationship.update_invite` to update contributor invite
  permissions for a redditor.
* :meth:`.LiveThread.discussions` to get submissions linking to the thread.
* :meth:`.LiveThread.report` to report the thread violating the Reddit rules.
* :meth:`.LiveHelper.now` to get the currently featured live thread.
* :meth:`.LiveHelper.info` to fetch information about each live thread in live thread
  IDs.

**Fixed**

* Uploading an image resulting in too large of a request (>500 KB) now raises
  ``prawcore.TooLarge`` instead of an ``AssertionError``.
* Uploading an invalid image raises ``APIException``.
* :class:`.Redditor` instances obtained via :attr:`.moderator` (e.g.,
  ``reddit.subreddit("subreddit").moderator()``) will contain attributes with the
  relationship metadata (e.g., ``mod_permissions``).
* :class:`.Message` instances retrieved from the inbox now have attributes ``author``,
  ``dest`` ``replies`` and ``subreddit`` properly converted to their appropriate PRAW
  model.

4.3.0 (2017/01/19)
------------------

**Added**

* :meth:`.LiveContributorRelationship.leave` to abdicate the live thread contributor
  position.
* :meth:`.LiveContributorRelationship.remove` to remove the redditor from the live
  thread contributors.
* :meth:`.limits` to provide insight into number of requests made and remaining in the
  current rate limit window.
* :attr:`.LiveThread.contrib` to obtain an instance of :class:`.LiveThreadContribution`.
* :meth:`.LiveThreadContribution.add` to add an update to the live thread.
* :meth:`.LiveThreadContribution.close` to close the live thread permanently.
* :attr:`.LiveUpdate.contrib` to obtain an instance of :class:`.LiveUpdateContribution`.
* :meth:`.LiveUpdateContribution.remove` to remove a live update.
* :meth:`.LiveContributorRelationship.accept_invite` to accept an invite to contribute
  the live thread.
* :meth:`.SubredditHelper.create` and :meth:`.SubredditModeration.update` have
  documented support for ``spoilers_enabled``. Note, however, that
  :meth:`.SubredditModeration.update` will currently unset the ``spoilers_enabled``
  value until such a time that Reddit returns the value along with the other settings.
* :meth:`.spoiler` and :meth:`.unspoiler` to change a submission's spoiler status.

**Fixed**

* :meth:`.LiveContributorRelationship.invite` and
  :meth:`.LiveContributorRelationship.remove_invite` now hit endpoints, which starts
  with "api/", for consistency.
* :meth:`.ModeratorRelationship.update`, and
  :meth:`.ModeratorRelationship.update_invite` now always remove known unlisted
  permissions.

4.2.0 (2017/01/07)
------------------

**Added**

* ``.Subreddit.rules`` to get the rules of a subreddit.
* :class:`.LiveContributorRelationship`, which can be obtained through
  :attr:`.LiveThread.contributor`, to interact with live threads' contributors.
* :meth:`~.ModeratorRelationship.remove_invite` to remove a moderator invite.
* :meth:`.LiveContributorRelationship.invite` to send a contributor invitation.
* :meth:`.LiveContributorRelationship.remove_invite` to remove the contributor
  invitation.

**Deprecated**

* Return values from :meth:`.Comment.block`, :meth:`.Message.block`,
  :meth:`.SubredditMessage.block`, :meth:`.SubredditFlair.delete`, :meth:`.friend`,
  :meth:`.Redditor.message`, :meth:`.Subreddit.message`, :meth:`.select`, and
  :meth:`.unfriend` will be removed in PRAW 5 as they do not provide any useful
  information.

**Fixed**

* :meth:`.hide()` and :meth:`.unhide()` now accept a list of additional submissions.
* :meth:`.replace_more` is now recoverable. Previously, when an exception was raised
  during the work done by :meth:`.replace_more`, all unreplaced :class:`.MoreComments`
  instances were lost. Now :class:`.MoreComments` instances are only removed once their
  children have been added to the :class:`.CommentForest` enabling callers of
  :meth:`.replace_more` to call the method as many times as required to complete the
  replacement.
* Working with contributors on :class:`.SubredditWiki` is done consistently through
  ``contributor`` not ``contributors``.
* ``Subreddit.moderator()`` works.
* ``live_thread.contributor()`` now returns :class:`.RedditorList` correctly.

**Removed**

* ``validate_time_filter`` is no longer part of the public interface.

4.1.0 (2016/12/24)
------------------

**Added**

* :meth:`praw.models.Subreddits.search_by_topic` to search subreddits by topic. (see:
  https://www.reddit.com/dev/api/#GET_api_subreddits_by_topic).
* :meth:`praw.models.LiveHelper.__call__` to provide interface to
  ``praw.models.LiveThread.__init__``.
* :class:`.SubredditFilters` to work with filters for special subreddits, like
  ``r/all``.
* Added callables for :class:`.SubredditRelationship` and :class:`.SubredditFlair` so
  that ``limit`` and other parameters can be passed.
* Add :meth:`~praw.models.Message.reply` to :class:`.Message` which was accidentally
  missed previously.
* Add ``sticky`` parameter to :meth:`.CommentModeration.distinguish` to sticky comments.
* :meth:`.flair` to add a submission's flair from an instance of :class:`.Submission`.
* :meth:`.Comment.parent` to obtain the parent of a :class:`.Comment`.
* :meth:`.opt_in` and :meth:`.opt_out` to :class:`.Subreddit` to permit working with
  quarantined subreddits.
* :class:`.LiveUpdate` to represent an individual update in a :class:`.LiveThread`.
* Ability to access an individual :class:`.LiveUpdate` via
  ``reddit.live("THREAD_ID")["UPDATE_ID"]``.
* :meth:`.LiveThread.updates` to iterate the updates of the thread.

**Changed**

* :meth:`.me` now caches its result in order to reduce redundant requests for methods
  that depend on it. Set ``use_cache=False`` when calling to bypass the cache.
* :meth:`.replace_more` can be called on :class:`.Comment` ``replies``.

**Deprecated**

* ``validate_time_filter`` will be removed from the public interface in PRAW 4.2 as it
  was never intended to be part of it to begin with.
* Iterating directly over :class:`.SubredditRelationship` (e.g., ``subreddit.banned``,
  ``subreddit.contributor``, ``subreddit.moderator``, etc) and :class:`.SubredditFlair`
  will be removed in PRAW 5. Iterate instead over their callables, e.g.
  ``subreddit.banned()`` and ``subreddit.flair()``.
* The following methods are deprecated to be removed in PRAW 5 and are replaced with
  similar ``Comment.mod...`` and ``Submission.mod...`` alternatives:
  ``Subreddit.mod.approve``, ``Subreddit.mod.distinguish``,
  ``Subreddit.mod.ignore_reports``, ``Subreddit.mod.remove``,
  ``Subreddit.mod.undistinguish``, ``Subreddit.mod.unignore_reports``.
* Support for passing a :class:`.Submission` to :meth:`.SubredditFlair.set` will be
  removed in PRAW 5. Use :meth:`.flair` instead.
* The ``thing`` argument to :meth:`.SubredditFlair.set` is replaced with ``redditor``
  and will be removed in PRAW 5.

**Fixed**

* :meth:`.SubredditModeration.update` accurately updates ``exclude_banned_modqueue``,
  ``header_hover_text``, ``show_media`` and ``show_media_preview`` values.
* Instances of :class:`.Comment` obtained through the inbox (including mentions) are now
  refreshable.
* Searching ``r/all`` should now work as intended for all users.
* Accessing an invalid attribute on an instance of :class:`.Message` will raise
  :py:class:`AttributeError` instead of :class:`.PRAWException`.

4.0.0 (2016/11/29)
------------------

**Fixed**

* Fix bug where ipython tries to access attribute
  ``_ipython_canary_method_should_not_exist_`` resulting in a useless fetch.
* Fix bug where Comment replies becomes ``[]`` after attempting to access an invalid
  attribute on the Comment.
* Reddit.wiki[...] converts the passed in page name to lower case as pages are only
  saved in lower case and non-lower case page names results in a Redirect exception
  (thanks pcjonathan).

4.0.0rc3 (2016/11/26)
---------------------

**Added**

* ``implicit`` parameter to :meth:`.url` to support the implicit flow for **installed**
  applications (see:
  https://github.com/reddit/reddit/wiki/OAuth2#authorization-implicit-grant-flow)
* :meth:`.scopes` to discover which scopes are available to the current authentication
* Lots of documentation: https://praw.readthedocs.io/

4.0.0rc2 (2016/11/20)
---------------------

**Fixed**

* :meth:`~praw.models.Auth.authorize` properly sets the session's Authentication (thanks
  @williammck).

4.0.0rc1 (2016/11/20)
---------------------

PRAW 4 introduces significant breaking changes. The numerous changes are not listed
here, only the feature removals. Please read through :doc:`/getting_started/quick_start`
to help with updating your code to PRAW 4. If you require additional help please ask on
`r/redditdev <https://www.reddit.com/r/redditdev>`_ or via Slack.

**Added**

* :meth:`praw.models.Comment.block`, :meth:`praw.models.Message.block`, and
  :meth:`praw.models.SubredditMessage.block` to permit blocking unwanted user contact.
* :meth:`praw.models.LiveHelper.create` to create new live threads.
* :meth:`praw.models.Redditor.unblock` to undo a block.
* :meth:`praw.models.Subreddits.gold` to iterate through gold subreddits.
* :meth:`praw.models.Subreddits.search` to search for subreddits by name and
  description.
* :meth:`praw.models.Subreddits.stream` to obtain newly created subreddits in near-
  realtime.
* :meth:`praw.models.User.karma` to retrieve the current user's subreddit karma.
* ``praw.models.reddit.submission.SubmissionModeration.lock`` and
  ``praw.models.reddit.submission.SubmissionModeration.unlock`` to change a Submission's
  lock state.
* :meth:`praw.models.reddit.subreddit.SubredditFlairTemplates.delete` to delete a single
  flair template.
* :meth:`praw.models.reddit.subreddit.SubredditModeration.unread` to iterate over unread
  moderation messages.
* :meth:`praw.models.reddit.subreddit.ModeratorRelationship.invite` to invite a
  moderator to a subreddit.
* :meth:`praw.models.reddit.subreddit.ModeratorRelationship.update` to update a
  moderator's permissions.
* :meth:`praw.models.reddit.subreddit.ModeratorRelationship.update_invite` to update an
  invited moderator's permissions.
* :meth:`praw.models.Front.random_rising`, :meth:`praw.models.Subreddit.random_rising`
  and :meth:`praw.models.Multireddit.random_rising`.
* :class:`~.WikiPage` supports a revision argument.
* :meth:`~.SubredditWiki.revisions` to obtain a list of recent revisions to a subreddit.
* :meth:`~.WikiPage.revisions` to obtain a list of revisions for a wiki page.
* Support installed-type OAuth apps.
* Support read-only OAuth for all application types.
* Support script-type OAuth apps.


**Changed**

.. note::

    Only prominent changes are listed here.

* ``helpers.comments_stream`` is now
  :meth:`praw.models.reddit.subreddit.SubredditStream.comments`
* ``helpers.submissions_between`` is now ``Subreddit.submissions``. This new method now
  only iterates through newest submissions first and as a result makes approximately 33%
  fewer requests.
* ``helpers.submission_stream`` is now
  :meth:`praw.models.reddit.subreddit.SubredditStream.submissions`

**Removed**

* Removed :class:`.Reddit`'s ``login`` method. Authentication must be done through
  OAuth.
* Removed ``praw-multiprocess`` as this functionality is no longer needed with PRAW 4.
* Removed non-oauth functions ``Message.collapse`` and ``Message.uncollapse``
  ``is_username_available``.
* Removed captcha related functions.


For changes prior to version 4.0 please see: `3.4.0 changelog
<https://praw.readthedocs.io/en/v3.4.0/pages/changelog.html>`_
