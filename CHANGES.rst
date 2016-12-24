Change Log
==========

4.1.0 (2016/12/24)
------------------

**Added**

* :meth:`praw.models.Subreddits.search_by_topic` to search subreddits by topic.
  (see: https://www.reddit.com/dev/api/#GET_api_subreddits_by_topic).
* :meth:`praw.models.LiveHelper.__call__` to provide interface to
  `praw.models.LiveThread.__init__`.
* :class:`.SubredditFilters` to work with filters for special subreddits, like
  ``/r/all``.
* Added callables for :class:`.SubredditRelationship` and
  :class:`.SubredditFlair` so that ``limit`` and other parameters can be passed.
* Add :meth:`~praw.models.Message.reply` to :class:`.Message` which was
  accidentally missed previously.
* Add `sticky` parameter to :meth:`.CommentModeration.distinguish` to sticky
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
  4.1+ as it was never intended to be part of it to begin with.
* Iterating directly over :class:`.SubredditRelationship` (e.g.,
  ``subreddit.banned``, ``subreddit.contributor``, ``subreddit.moderator``, etc)
  and :class:`.SubredditFlair` will be removed in PRAW 5. Iterate instead over
  their callables, e.g. ``subreddit.banned()`` and ``subreddit.flair()``.
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
* Fix bug where Comment replies becomes `[]` after attempting to access an
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
* Removed `praw-multiprocess` as this functionality is no longer needed with
  PRAW 4.
* Removed non-oauth functions ``Message.collapse`` and ``Message.uncollapse``
  ``is_username_available``.
* Removed captcha related functions.


For changes prior to version 4.0 please see: `3.4.0 changelog
<http://praw.readthedocs.io/en/v3.4.0/pages/changelog.html>`_
