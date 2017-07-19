Change Log
==========

Unreleased
----------

**Added**

* :attr:`.Redditor.stream`, with methods :meth:`.RedditorStream.submissions()`
  and :meth:`.RedditorStream.comments()` to stream a Redditor's
  comments or submissions
* :class:`.RedditorStream` has been added to facilitate
  :attr:`.Redditor.stream`


5.0.1 (2017/07/11)
------------------

**Fixed**

* Calls to :meth:`.hide()` and :meth:`.unhide()` properly batch into requests
  of 50 submissions at a time.
* Lowered the average maximum delay between inactive stream checks by 4x to 16
  seconds. It was previously 64 seconds, which was too long.

5.0.0 (2017/07/04)
------------------

**Added**

* :meth:`.Comment.disable_inbox_replies`, :meth:`.Comment.enable_inbox_replies`
  :meth:`.Submission.disable_inbox_replies`, and
  :meth:`.Submission.enable_inbox_replies` to toggle inbox replies on comments
  and submissions.

**Changed**

* ``cloudsearch`` is no longer the default syntax for
  :meth:`.Subreddit.search`. ``lucene`` is now the default
  syntax so that PRAW's default is aligned with Reddit's default.
* :meth:`.Reddit.info` will now take either a list of fullnames
  or a single URL string.
* :meth:`.Subreddit.submit` accepts a flair template ID and text.

**Fixed**

* Fix accessing :attr:`.LiveUpdate.contrib` raises ``AttributeError``.

**Removed**

* Iterating directly over :class:`.SubredditRelationship` (e.g.,
  ``subreddit.banned``, ``subreddit.contributor``, ``subreddit.moderator``,
  etc) and :class:`.SubredditFlair` is no longer possible. Iterate instead over
  their callables, e.g. ``subreddit.banned()`` and ``subreddit.flair()``.
* The following methods are removed:
  ``Subreddit.mod.approve``, ``Subreddit.mod.distinguish``,
  ``Subreddit.mod.ignore_reports``, ``Subreddit.mod.remove``,
  ``Subreddit.mod.undistinguish``, ``Subreddit.mod.unignore_reports``.
* Support for passing a :class:`.Submission` to :meth:`.SubredditFlair.set`
  is removed.
* The ``thing`` argument to :meth:`.SubredditFlair.set` is removed.
* Return values from :meth:`.Comment.block`, :meth:`.Message.block`,
  :meth:`.SubredditMessage.block`, :meth:`.SubredditFlair.delete`,
  :meth:`.friend`, :meth:`.Redditor.message`, :meth:`.Subreddit.message`,
  :meth:`.select`, and :meth:`.unfriend` are removed as they do not provide
  any useful information.
* ``praw.ini`` no longer reads in ``http_proxy`` and ``https_proxy`` settings.
* ``is_link`` parameter of :meth:`.SubredditRedditorFlairTemplates.add` and
  :meth:`.SubredditRedditorFlairTemplates.clear`. Use
  :class:`.SubredditLinkFlairTemplates` instead.

4.6.0 (2017/07/04)
------------------

The release's sole purpose is to announce the deprecation of the ``is_link``
parameter as described below:

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

* :meth:`~praw.models.reddit.subreddit.Modmail.unread_count` to get unread
  count by conversation state.
* :meth:`~praw.models.reddit.subreddit.Modmail.bulk_read` to mark conversations
  as read by conversation state.
* :meth:`~praw.models.reddit.subreddit.Modmail.subreddits` to fetch subreddits
  using new modmail.
* :meth:`~praw.models.reddit.subreddit.Modmail.create` to create a new modmail
  conversation.
* :meth:`~praw.models.ModmailConversation.read` to mark modmail conversations
  as read.
* :meth:`~praw.models.ModmailConversation.unread` to mark modmail conversations
  as unread.
* :meth:`~praw.models.reddit.subreddit.Modmail.conversations` to get new
  modmail conversations.
* :meth:`~praw.models.ModmailConversation.highlight` to highlight modmail
  conversations.
* :meth:`~praw.models.ModmailConversation.unhighlight` to unhighlight modmail
  conversations.
* :meth:`~praw.models.ModmailConversation.mute` to mute modmail conversations.
* :meth:`~praw.models.ModmailConversation.unmute` to unmute modmail
  conversations.
* :meth:`~praw.models.ModmailConversation.archive` to archive modmail
  conversations.
* :meth:`~praw.models.ModmailConversation.unarchive` to unarchive modmail
  conversations.
* :meth:`~praw.models.ModmailConversation.reply` to reply to modmail
  conversations.
* :meth:`~praw.models.reddit.subreddit.Modmail.__call__` to get a new modmail
  conversation.
* :meth:`.Inbox.stream` to stream new items in the inbox.
* Exponential request delay to all streams when no new items are returned in a
  request. The maximum delay between requests is 66 seconds.

**Changed**

* :meth:`.submit` accepts ``selftext=''`` to create a title-only submission.
* :class:`.Reddit` accepts ``requestor_class=cls`` for a customized requestor
  class and ``requestor_kwargs={'param': value}`` for passing arguments to
  requestor initialization.
* :meth:`~praw.models.reddit.subreddit.SubredditStream.comments`,
  :meth:`~praw.models.reddit.subreddit.SubredditStream.submissions`, and
  :meth:`~praw.models.Subreddits.stream` accept a ``pause_after`` argument to
  allow pausing of the stream. The default value of ``None`` retains the
  preexisting behavior.

**Deprecated**

* ``cloudsearch`` will no longer be the default syntax for
  :meth:`.Subreddit.search` in PRAW 5. Instead ``lucene`` will be the default
  syntax so that PRAW's default is aligned with Reddit's default.

**Fixed**

* Fix bug where :class:`.WikiPage` revisions with deleted authors caused
  ``TypeError``.
* :class:`.Submission` attributes ``comment_limit`` and ``comment_sort``
  maintain their values after making instances non-lazy.

4.4.0 (2017/02/21)
------------------

**Added**

* :meth:`.LiveThreadContribution.update` to update settings of a live thread.
* ``reset_timestamp`` to :attr:`.limits` to provide insight into when the
  current rate limit window will expire.
* :meth:`.upload_mobile_header` to upload subreddit mobile header.
* :meth:`.upload_mobile_icon` to upload subreddit mobile icon.
* :meth:`.delete_mobile_header` to remove subreddit mobile header.
* :meth:`.delete_mobile_icon` to remove subreddit mobile icon.
* :meth:`.LiveUpdateContribution.strike` to strike a content of a live thread.
* :meth:`.LiveContributorRelationship.update` to update contributor
  permissions for a redditor.
* :meth:`.LiveContributorRelationship.update_invite` to update contributor
  invite permissions for a redditor.
* :meth:`.LiveThread.discussions` to get submissions linking to the thread.
* :meth:`.LiveThread.report` to report the thread violating the Reddit rules.
* :meth:`.LiveHelper.now` to get the currently featured live thread.
* :meth:`.LiveHelper.info` to fetch information about each live thread in
  live thread IDs.

**Fixed**

* Uploading an image resulting in too large of a request (>500 KB) now
  raises ``prawcore.TooLarge`` instead of an ``AssertionError``.
* Uploading an invalid image raises :class:`.APIException`.
* :class:`.Redditor` instances obtained via :attr:`.moderator` (e.g.,
  ``reddit.subreddit('subreddit').moderator()``) will contain attributes with
  the relationship metadata (e.g., ``mod_permissions``).
* :class:`.Message` instances retrieved from the inbox now have attributes
  ``author``, ``dest`` ``replies`` and ``subreddit`` properly converted to
  their appropriate PRAW model.

4.3.0 (2017/01/19)
------------------

**Added**

* :meth:`.LiveContributorRelationship.leave` to abdicate the live thread
  contributor position.
* :meth:`.LiveContributorRelationship.remove` to remove the redditor
  from the live thread contributors.
* :attr:`.limits` to provide insight into number of requests made and remaining
  in the current rate limit window.
* :attr:`.LiveThread.contrib` to obtain an instance of
  :class:`.LiveThreadContribution`.
* :meth:`.LiveThreadContribution.add` to add an update to the live thread.
* :meth:`.LiveThreadContribution.close` to close the live thread permanently.
* :attr:`.LiveUpdate.contrib` to obtain an instance of
  :class:`.LiveUpdateContribution`.
* :meth:`.LiveUpdateContribution.remove` to remove a live update.
* :meth:`.LiveContributorRelationship.accept_invite` to accept an invite to
  contribute the live thread.
* :meth:`.SubredditHelper.create` and :meth:`.SubredditModeration.update` have
  documented support for ``spoilers_enabled``. Note, however, that
  :meth:`.SubredditModeration.update` will currently unset the
  ``spoilers_enabled`` value until such a time that Reddit returns the value
  along with the other settings.
* :meth:`.spoiler` and :meth:`.unspoiler` to change a submission's spoiler
  status.

**Fixed**

* :meth:`.LiveContributorRelationship.invite` and
  :meth:`.LiveContributorRelationship.remove_invite` now hit endpoints,
  which starts with 'api/', for consistency.
* :meth:`.ModeratorRelationship.update`, and
  :meth:`.ModeratorRelationship.update_invite` now always remove known unlisted
  permissions.

4.2.0 (2017/01/07)
------------------

**Added**

* :meth:`.Subreddit.rules` to get the rules of a subreddit.
* :class:`.LiveContributorRelationship`, which can be obtained through
  :attr:`.LiveThread.contributor`, to interact with live threads'
  contributors.
* :meth:`~.ModeratorRelationship.remove_invite` to remove a moderator invite.
* :meth:`.LiveContributorRelationship.invite` to send a contributor invitation.
* :meth:`.LiveContributorRelationship.remove_invite` to remove the contributor
  invitation.

**Deprecated**

* Return values from :meth:`.Comment.block`, :meth:`.Message.block`,
  :meth:`.SubredditMessage.block`, :meth:`.SubredditFlair.delete`,
  :meth:`.friend`, :meth:`.Redditor.message`, :meth:`.Subreddit.message`,
  :meth:`.select`, and :meth:`.unfriend` will be removed in PRAW 5 as they do
  not provide any useful information.

**Fixed**

* :meth:`.hide()` and :meth:`.unhide()` now accept a list of additional
  submissions.
* :meth:`.replace_more` is now recoverable. Previously, when an exception was
  raised during the work done by :meth:`.replace_more`, all unreplaced
  :class:`.MoreComments` instances were lost. Now :class:`.MoreComments`
  instances are only removed once their children have been added to the
  :class:`.CommentForest` enabling callers of :meth:`.replace_more` to call the
  method as many times as required to complete the replacement.
* Working with contributors on :class:`.SubredditWiki` is done consistently
  through ``contributor`` not ``contributors``.
* ``Subreddit.moderator()`` works.
* ``live_thread.contributor()`` now returns :class:`.RedditorList` correctly.

**Removed**

* ``validate_time_filter`` is no longer part of the public interface.

4.1.0 (2016/12/24)
------------------

**Added**

* :meth:`praw.models.Subreddits.search_by_topic` to search subreddits by topic.
  (see: https://www.reddit.com/dev/api/#GET_api_subreddits_by_topic).
* :meth:`praw.models.LiveHelper.__call__` to provide interface to
  ``praw.models.LiveThread.__init__``.
* :class:`.SubredditFilters` to work with filters for special subreddits, like
  ``/r/all``.
* Added callables for :class:`.SubredditRelationship` and
  :class:`.SubredditFlair` so that ``limit`` and other parameters can be
  passed.
* Add :meth:`~praw.models.Message.reply` to :class:`.Message` which was
  accidentally missed previously.
* Add ``sticky`` parameter to :meth:`.CommentModeration.distinguish` to sticky
  comments.
* :meth:`.flair` to add a submission's flair from an instance of
  :class:`.Submission`.
* :meth:`.Comment.parent` to obtain the parent of a :class:`.Comment`.
* :meth:`.opt_in` and :meth:`.opt_out` to :class:`.Subreddit` to permit working
  with quarantined subreddits.
* :class:`.LiveUpdate` to represent an individual update in a
  :class:`.LiveThread`.
* Ability to access an individual :class:`.LiveUpdate` via
  ``reddit.live('THREAD_ID')['UPDATE_ID']``.
* :meth:`.LiveThread.updates` to iterate the updates of the thread.

**Changed**

* :meth:`.me` now caches its result in order to reduce redundant requests for
  methods that depend on it. Set ``use_cache=False`` when calling to bypass the
  cache.
* :meth:`.replace_more` can be called on :class:`.Comment` ``replies``.

**Deprecated**

* ``validate_time_filter`` will be removed from the public interface in PRAW
  4.2 as it was never intended to be part of it to begin with.
* Iterating directly over :class:`.SubredditRelationship` (e.g.,
  ``subreddit.banned``, ``subreddit.contributor``, ``subreddit.moderator``,
  etc) and :class:`.SubredditFlair` will be removed in PRAW 5. Iterate instead
  over their callables, e.g. ``subreddit.banned()`` and ``subreddit.flair()``.
* The following methods are deprecated to be removed in PRAW 5 and are replaced
  with similar ``Comment.mod...`` and ``Submission.mod...`` alternatives:
  ``Subreddit.mod.approve``, ``Subreddit.mod.distinguish``,
  ``Subreddit.mod.ignore_reports``, ``Subreddit.mod.remove``,
  ``Subreddit.mod.undistinguish``, ``Subreddit.mod.unignore_reports``.
* Support for passing a :class:`.Submission` to :meth:`.SubredditFlair.set`
  will be removed in PRAW 5. Use :meth:`.flair` instead.
* The ``thing`` argument to :meth:`.SubredditFlair.set` is replaced with
  ``redditor`` and will be removed in PRAW 5.

**Fixed**

* :meth:`.SubredditModeration.update` accurately updates
  ``exclude_banned_modqueue``, ``header_hover_text``, ``show_media`` and
  ``show_media_preview`` values.
* Instances of :class:`.Comment` obtained through the inbox (including
  mentions) are now refreshable.
* Searching ``/r/all`` should now work as intended for all users.
* Accessing an invalid attribute on an instance of :class:`.Message` will raise
  :py:class:`.AttributeError` instead of :class:`.PRAWException`.

4.0.0 (2016/11/29)
------------------

**Fixed**

* Fix bug where ipython tries to access attribute
  ``_ipython_canary_method_should_not_exist_`` resulting in a useless fetch.
* Fix bug where Comment replies becomes ``[]`` after attempting to access an
  invalid attribute on the Comment.
* Reddit.wiki[...] converts the passed in page name to lower case as pages are
  only saved in lower case and non-lower case page names results in a Redirect
  exception (thanks pcjonathan).

4.0.0rc3 (2016/11/26)
---------------------

**Added**

* ``implicit`` parameter to :meth:`.url` to support the implicit flow for
  **installed** applications (see:
  https://github.com/reddit/reddit/wiki/OAuth2#authorization-implicit-grant-flow)
* :meth:`.scopes` to discover which scopes are available to the current
  authentication
* Lots of documentation: http://praw.readthedocs.io/

4.0.0rc2 (2016/11/20)
---------------------

**Fixed**

* :meth:`~praw.models.Auth.authorize` properly sets the session's
  Authentication (thanks @williammck).

4.0.0rc1 (2016/11/20)
---------------------

PRAW 4 introduces significant breaking changes. The numerous changes are not
listed here, only the feature removals. Please read through
:doc:`/getting_started/quick_start` to help with updating your code to
PRAW 4. If you require additional help please ask on `/r/redditdev
<https://www.reddit.com/r/redditdev>`_ or in the `praw-dev/praw
<https://gitter.im/praw-dev/praw>`_ channel on gitter.

**Added**

* :meth:`praw.models.Comment.block`, :meth:`praw.models.Message.block`, and
  :meth:`praw.models.SubredditMessage.block` to permit blocking unwanted user
  contact.
* :meth:`praw.models.LiveHelper.create` to create new live threads.
* :meth:`praw.models.Redditor.unblock` to undo a block.
* :meth:`praw.models.Subreddits.gold` to iterate through gold subreddits.
* :meth:`praw.models.Subreddits.search` to search for subreddits by name and
  description.
* :meth:`praw.models.Subreddits.stream` to obtain newly created subreddits in
  near-realtime.
* :meth:`praw.models.User.karma` to retrieve the current user's subreddit
  karma.
* :meth:`praw.models.reddit.submission.SubmissionModeration.lock` and
  :meth:`praw.models.reddit.submission.SubmissionModeration.unlock` to change a
  Submission's lock state.
* :meth:`praw.models.reddit.subreddit.SubredditFlairTemplates.delete` to
  delete a single flair template.
* :meth:`praw.models.reddit.subreddit.SubredditModeration.unread` to iterate
  over unread moderation messages.
* :meth:`praw.models.reddit.subreddit.ModeratorRelationship.invite` to invite a
  moderator to a subreddit.
* :meth:`praw.models.reddit.subreddit.ModeratorRelationship.update` to update a
  moderator's permissions.
* :meth:`praw.models.reddit.subreddit.ModeratorRelationship.update_invite` to
  update an invited moderator's permissions.
* :meth:`praw.models.Front.random_rising`,
  :meth:`praw.models.Subreddit.random_rising` and
  :meth:`praw.models.Multireddit.random_rising`.
* :class:`~.WikiPage` supports a revision argument.
* :meth:`~.SubredditWiki.revisions` to obtain a list of recent revisions to a
  subreddit.
* :meth:`~.WikiPage.revisions` to obtain a list of revisions for a wiki
  page.
* Support installed-type OAuth apps.
* Support read-only OAuth for all application types.
* Support script-type OAuth apps.


**Changed**

.. note:: Only prominent changes are listed here.

* ``helpers.comments_stream`` is now
  :meth:`praw.models.reddit.subreddit.SubredditStream.comments`
* ``helpers.submissions_between`` is now
  :meth:`praw.models.Subreddit.submissions`. This new method now only iterates
  through newest submissions first and as a result makes approximately 33%
  fewer requests.
* ``helpers.submission_stream`` is now
  :meth:`praw.models.reddit.subreddit.SubredditStream.submissions`

**Removed**

* Removed :class:`.Reddit`'s ``login`` method. Authentication must be done
  through OAuth.
* Removed ``praw-multiprocess`` as this functionality is no longer needed with
  PRAW 4.
* Removed non-oauth functions ``Message.collapse`` and ``Message.uncollapse``
  ``is_username_available``.
* Removed captcha related functions.


For changes prior to version 4.0 please see: `3.4.0 changelog
<http://praw.readthedocs.io/en/v3.4.0/pages/changelog.html>`_
