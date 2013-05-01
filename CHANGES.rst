Changelog
=========

This is the changelog for the released versions of PRAW. These changes are
divided into four categories.

 * **[FEATURE]** Something new has been added.
 * **[BUGFIX]** Something was broken before, but is now fixed.
 * **[REDDIT]** A change caused by an upstream change from reddit.
 * **[CHANGE]** Other changes affecting user programs, such as the renaming of
   a function.

Read `r/changelog <http://www.reddit.com/r/changelog>`_ to be notified of
upstream changes.

PRAW 2.1.1 (Unreleased)
-----------------------
 * **[FEATURE]** Added :meth:`praw.helpers.comment_stream` to provide a
   neverending stream of new comments.
 * **[BUGFIX]** Don't cache requests whose responses will result in an
   exception. This bug was introduced in version 2.1.0.

PRAW 2.1.0
----------
 * **[FEATURE]** PRAW now supports proper rate-limiting and shared caching when
   running multiple processes. See :ref:`multiprocess` for usage information.
 * **[CHANGE]** Remove explicit ``limit`` parameters from functions that
   utilize :meth:`.get_content` but don't alter the limit. This change will
   result in broken code if the calling code utilizes positional instead of
   keyword arguments.
 * **[CHANGE]** :meth:`~.UnauthenticatedReddit.get_flair` returns ``None`` when
   the redditor does not exist.
 * **[CHANGE]** Deprecated :meth:`.get_all_comments`. Use
   :meth:`~.UnauthenticatedReddit.get_comments` with ``all`` as the subreddit
   argument.
 * **[CHANGE]** Deprecated :meth:`.get_my_reddits`. Use
   :meth:`.get_my_subreddits` instead.
 * **[CHANGE]** Deprecated :meth:`.get_popular_reddits`. Use
   :meth:`.get_popular_subreddits` instead.
 * **[BUGFIX]** Allow editing non-top-level wiki pages fetched using
   :meth:`.Subreddit.get_wiki_page`.
 * **[BUGFIX]** Fix a bug in :meth:`~Subreddit.submit`. See
   https://github.com/praw-dev/praw/issues/213
 * **[BUGFIX]** Fix a python 3.3 bug in
   :meth:`~.Subreddit.upload_image`. See
   https://github.com/praw-dev/praw/issues/211

PRAW 2.0.15
-----------
 * **[FEATURE]** PRAW can now use a proxy server, see `#206
   <https://github.com/praw-dev/praw/issues/206>`_. The parameter
   ``http_proxy`` (optional) has been added to the configuration file to define
   a proxy server in the form host:ip or http://login:user@host:ip.


PRAW 2.0.14
-----------
 * **[BUGFIX]** Prevent potential invalid redirect exception when using
   :meth:`~.Subreddit.get_wiki_page`.


PRAW 2.0.13
-----------

 * **[FEATURE]** Added :meth:`.get_submissions` to batch convert fullnames
   (``t3_bas36id``) into :class:`.Submission` objects.
 * **[FEATURE]** Added :meth:`~.Subreddit.get_wiki_banned` to get a list of
   wiki banned users.
 * **[FEATURE]** Added :meth:`.add_wiki_ban` and
   :meth:`.remove_wiki_ban` to manage the list of wiki banned users.
 * **[FEATURE]** Added :meth:`~.Subreddit.get_wiki_contributors` to get a list
   of wiki contributors.
 * **[FEATURE]** Added :meth:`.add_wiki_contributor` and
   :meth:`.remove_wiki_contributor` to manage the list of wiki contributors.
 * **[FEATURE]** Added :meth:`~.Subreddit.get_wiki_page` to fetch an individual
   WikiPage
 * **[FEATURE]** Added :meth:`~.Subreddit.get_wiki_pages` to get a list of
   WikiPage objects.
 * **[FEATURE]** Wiki pages can be edited through either the
   :meth:`.WikiPage.edit` method of an already existing WikiPage object, or
   through the :meth:`~.Subreddit.edit_wiki_page` function.
   :meth:`~.Subreddit.edit_wiki_page` is also used to create new wiki pages.
 * **[CHANGE]** Deprecated :meth:`.ban`, :meth:`.unban`,
   :meth:`.make_contributor`, and :meth:`.make_moderator` in favor of the
   consistently named :meth:`.add_ban`, :meth:`.remove_ban`,
   :meth:`.add_contributor`, and :meth:`.add_moderator` respectively.


PRAW 2.0.12
-----------

 * **[FEATURE]** PRAW can now decode HTML entities, see `#186
   <https://github.com/praw-dev/praw/issues/186>`_. The parameter
   ``decode_html_entities`` (default ``False``) has been added to the
   configuration file to control whether this feature is activated.
 * **[FEATURE]** Add :exc:`.InvalidSubreddit` exception which is raised when
   attempting to get a listing for a nonexistent subreddit.
 * **[FEATURE]** All functions that use the :meth:`.get_content` generator
   function now take ``*args, **kwargs``.
 * **[BUGFIX]** Requesting user specific data such as :meth:`.get_unread` while
   OAuthenticated as a user, then switching OAuthentication to another user and
   re-requesting the data within ``cache_timeout`` would return the cached
   results matching the previously authenticated user.
 * **[BUGFIX]** :meth:`.friend` and :meth:`.unfriend` used to raise an
   ``AttributeError`` when called without user/pswd authentication. It now
   properly raises :exc:`.LoginRequired`.

PRAW 2.0.11
-----------

 * **[FEATURE]** Add the ``raise_captcha_exception`` argument to
   :obj:`.RequireCaptcha` decorator.  When ``raise_captcha_exception`` is
   ``True`` (default ``False``), PRAW wil not prompt for the captcha
   information but instead raise a :exc:`.InvalidCaptcha` exception.
 * **[REDDIT]** An `upstream change
   <http://www.reddit.com/r/changelog/comments/191ngp/
   reddit_change_rising_is_now_its_own_tab_instead/>`_
   has split new and rising into their own independent listings. Use the new
   :meth:`.get_rising` method instead of the old :meth:`.get_new_by_rising` and
   :meth:`~.Subreddit.get_new` instead of :meth:`.get_new_by_date`.
 * **[CHANGE]** The dependency on ``update_checker`` has been increased from >=
   0.4 to >= 0.5
 * **[BUGFIX]** After inviting a moderator invite, the cached set of moderated
   subreddits would not be updated with the new subreddit. Causing
   :func:`.restrict_access` to prevent performing moderater actions in the
   subreddit.

PRAW 2.0.10
-----------

 * **[FEATURE]** Add :meth:`~.Subreddit.delete_flair` method to
   :class:`.Subreddit` and :class:`.Reddit` objects.

PRAW 2.0.9
----------

 * **[FEATURE]** Add parameter ``update_user`` (default False) to
   :meth:`.get_unread` if it and ``unset_has_mail`` are both True, then the
   ``user`` object in the :class:`.Reddit` object will have it's ``has_mail``
   attribute set to ``False``.
 * **[FEATURE]** Add :meth:`.get_friends` and :meth:`.get_blocked` to
   :class:`.LoggedInRedditor`.
 * **[FEATURE]** Add the *read* scope to :meth:`.get_all_comments` in the
   :class:`.Reddit` object.
 * **[FEATURE]** Add the *read* scope to :meth:`~.Subreddit.get_comments` and
   the subreddit listings such as :meth:`~.Subreddit.get_new` in the
   :meth:`.Reddit` and :meth:`.Subreddit` object.
 * **[BUGFIX]** Fix bug in :meth:`.MoreComments.comments`.
 * **[CHANGE]** Break :meth:`.get_friends` and :meth:`~.Subreddit.get_banned`
   until there is an upstream fix to mean that does not require ssl for those
   endpoints.

PRAW 2.0.8
----------

 * **[FEATURE]** Add ``unset_has_mail`` parameter to :meth:`.get_unread`, if
   it's set to ``True``, then it will set ``has_mail`` for the logged-in user
   to ``False``.

PRAW 2.0.7
----------

 * **[REDDIT]** A `reddit update <`http://redd.it/17oer0>`_ broke PRAW's
   ability to use :meth:`.login` if it was authenticated as a logged-in user.
   This update adds the ability to re-login.
 * **[CHANGE]** :meth:`~.Subreddit.get_flair_list` can now be used when
   logged-in as a regular user, being logged in as a mod of the subreddit is no
   longer required.

PRAW 2.0.6
----------

 * **[FEATURE]** Add the :meth:`~.Subreddit.get_unmoderated` method to
   :class:`.Subreddit` and base reddit objects. This returns a listings of
   submissions that haven't been approved/removed by a moderator.


PRAW 2.0.5
----------

 * **[FEATURE]** Add the parameter ``gilded_only`` to
   :meth:`~.Subreddit.get_comments` and :meth:`.get_all_comments` methods in
   :class:`.Subreddit` and base reddit objects. If ``gilded_only`` is set to
   ``True``, then only gilded comments will be returned.
 * **[FEATURE]** Add :meth:`~.Reddit.get_comments` method to Reddit object. It
   works like :meth:`~.Subreddit.get_comments` in Subreddit objects except it
   takes the subreddit as the first argument.

PRAW 2.0.4
----------

 * **[BUGFIX]** Fix python 3 failure within the test suite introduced in 2.0.3.

PRAW 2.0.3
----------

 * **[FEATURE]** Add :meth:`~.Subreddit.delete_image` method to
   :class:`.Subreddit` objects (also callable on the base reddit object with
   the subreddit as the first argument):
 * **[CHANGE]** PRAW now requires version 0.4 of ``update_checker``.

PRAW 2.0.2
----------

 * **[BUGFIX]** Fixed bug when comparing :class:`.MoreComments` classes in
   Python 3.x

PRAW 2.0.1
----------

 * **[BUGFIX]** Fix bug with ``limit=None`` in method
   :meth:`.replace_more_comments` in :class:`.Submission` object.

PRAW 2.0.0
----------

 * **[FEATURE]** Support reddit OAuth2 scopes (passwordless authentication).
   See :ref:`oauth` for usage information.
 * **[FEATURE]** Maximize the number of items fetched when explicit limits are
   set thus reducing the number of requests up to 4x in some cases.
 * **[FEATURE]** Add the following API methods to :class:`.Subreddit` objects
   (also callable on the base reddit object with the subreddit as the first
   argument):

   * :meth:`~.Subreddit.accept_moderator_invite` -- accept a pending moderator
     invite
   * :meth:`~.Subreddit.get_mod_log`  -- return ModAction objects for each item
     (run vars(item), to see available attributes)
   * :meth:`~.Subreddit.configure_flair`  -- interface to subreddit flair
     options
   * :meth:`~.Subreddit.upload_image` -- upload an image for the subreddit
     header or use in CSS

 * **[FEATURE]** Support 'admin' distinguishing of items via
   :meth:`.distinguish`
 * **[FEATURE]** Ability to specify max-character limit for object-to-string
   representations via ``output_chars_limit`` in ``praw.ini``
 * **[CHANGE]** Remove ``comments_flat`` property of :class:`.Submission`
   objects. The new :meth:`praw.helpers.flatten_tree` can be used to flatten
   comment trees.
 * **[CHANGE]** Remove ``all_comments`` and ``all_comments_flat`` properties of
   Submission objects. The now public method :meth:`.replace_more_comments`
   must now be explicitly called to replace instances of :class:`.MoreComments`
   within the comment tree.
 * **[CHANGE]** The ``content_id`` attribute of :class:`.RedditContentObject`
   has been renamed to :attr:`.fullname`
 * **[CHANGE]** The ``info`` base Reddit instance method has been renamed to
   :meth:`.get_info`.
 * **[CHANGE]** ``get_saved_links`` has been renamed to :meth:`.get_saved` and
   moved to the :class:`.LoggedInRedditor` (``r.user``) namespace.
 * **[CHANGE]** The Subreddit ``get_info`` method has been renamed to
   :meth:`.from_url` and supports parameters for changing the number of
   comments to fetch and by what sort method.
 * **[CHANGE]** The :meth:`.get_submission` method also now supports parameters
   for changing the number of comments to fetch and by what sort method.
 * **[CHANGE]** :meth:`.mark_as_nsfw` and :meth:`.unmark_as_nsfw` can no longer
   be used on :class:`.Subreddit` objects. Use ``update_settings(nsfw=True)``
   instead.
 * **[CHANGE]** Remove depreciated method ``compose_message``.
 * **[CHANGE]** Refactored and add a number of exception classes (`docs
   <https://python-reddit-api-wrapper.readthedocs.org/en/latest/
   praw.html#module-praw.errors>`_,
   `source <https://github.com/praw-dev/praw/blob/master/praw/errors.py>`_)
   This includes the renaming of:

   * ``BadCaptcha`` to :exc:`.InvalidCaptcha`
   * ``NonExistantUser`` to :exc:`.InvalidUser`

 * **[CHANGE]** Simplify content-limit handling and remove the following
   no-longer necessary parameters from ``praw.ini``:

   * ``comment_limit``
   * ``comment_sort``
   * ``default_content_limit``
   * ``gold_comments_max``
   * ``more_comments_max``
   * ``regular_comments_max``

 * **[CHANGE]** Move the following methods from :class:`.LoggedInRedditor` to
   base reddit object.

   * :meth:`.get_unread`
   * :meth:`.get_inbox`
   * :meth:`.get_mod_mail`
   * :meth:`.get_sent`

PRAW 1.0.16
-----------

 * **[FEATURE]** Add support for r/random

PRAW 1.0.15
-----------

 * **[FEATURE]** Added the functions :meth:`.hide` and :meth:`.unhide` to
   :class:`.Submission`.
 * **[FEATURE]** Added function :meth:`.is_username_available` to
   :class:`.Reddit`.

PRAW 1.0.14
-----------

 * **[FEATURE]** Extended functionality to Python 3.3

PRAW 1.0.13
-----------

 * **[BUGFIX]** Fixed non-equality bug. Before comparing two PRAW objects with
   != would always return ``True``.
 * **[FEATURE]** Added the function ``my_contributions`` to
   :class:`.LoggedInRedditor`.  Use this to find the subreddits where the user
   is an approved contributor.
 * **[CHANGE]** Voting on something will now force the next call to
   :meth:`.get_liked` or :meth:`.get_disliked` to re-query from the reddit
   rather than use the cache.

PRAW 1.0.12
-----------

 * **[FEATURE]** Support for optional 'prev' values added.

PRAW 1.0.11
-----------

 * **[FEATURE]** Added :meth:`~.Subreddit.get_top` to :class:`.Reddit`.

PRAW 1.0.10
-----------

 * **[FEATURE]** Allow for the OS to not be identified when searching for
   ``praw.ini``.

PRAW 1.0.9
----------

 * **[FEATURE]** Added the functions :meth:`.mark_as_nsfw` and
   :meth:`.unmark_as_nsfw` to :class:`.Submission` and :class:`.Subreddit`.

PRAW 1.0.8
----------

 * **[CHANGE]** Printing a :class:`.Submission` to ``sys.stdout`` will now
   limit the output length to 80 chars, just like :class:`.Comment` does.
 * **[FEATURE]** The maximum amount of comments that can be retrieved alongside
   a submission for gold and regular accounts has been exported to
   ``praw.ini``.
 * **[REDDIT]** Checks for login/moderator in
   :meth:`~.Subreddit.get_moderators` and :meth:`~.Subreddit.get_flair` for
   Subreddit are no longer necessary.
 * **[FEATURE]** Added the function :meth:`.refresh` to :class:`.Submission`,
   :class:`.Subreddit` and :class:`.Redditor`. This will make PRAW re-query
   either reddit or the cache, depending on whether the last call was within
   ``cache_timeout``, for the latest values and update the objects values.
 * **[FEATURE]** Added functions :meth:`.get_liked`, :meth:`.get_disliked` and
   :meth:`.get_hidden` to :class:`.LoggedInRedditor` to allow you to get the
   Things the user has upvoted, downvoted or hidden.
 * **[BUGFIX]** Temporary bugfix until prevstyles become optional.
 * **[FEATURE]** Added prevstyle to set_stylesheet requests.
 * **[BUGFIX]** Putting in ``user`` or ``pswd`` to ``praw.ini`` without values
   will no longer make it impossible to login.
 * **[FEATURE]** You can now have just ``user`` filled out in ``praw.ini`` to
   ease login while remaining safe.

PRAW 1.0.7
----------

 * **[REDDIT]** New fields ``prev_description_id`` and
   ``prev_public_description_id`` added to :meth:`~.Subreddit.set_settings` as
   per the upstream change

PRAW 1.0.6
----------

 * **[CHANGE]** ``compose_message`` has been renamed to
   :meth:`~.PrivateMessagesMixin.send_message` in :class:`.Reddit` and
   :class:`.LoggedInRedditor`. ``compose_message`` is now depreciated and will
   be removed around the end of 2012.

PRAW 1.0.5
----------

 * **[FEATURE]** :meth:`.get_popular_reddits` added to :class:`.Reddit`.

PRAW 1.0.4
----------

 * **[FEATURE]** Added :meth:`~.UnauthenticatedReddit.get_new` and
   :meth:`~.UnauthenticatedReddit.get_controversial` to :class:`.Reddit`.

PRAW 1.0.3
----------

 * **[REDDIT]** The logged in / moderator checks for ``flair_list`` in
   :class:`.Reddit` are no longer needed and have been removed.

PRAW 1.0.2
----------

 * **[FEATURE]** :attr:`.score` property wrapped function have been added to
   :class:`.Comment`.

PRAW 1.0.1
----------

 * **[FEATURE]** ``require_moderator`` decorator now supports multi-reddits.
 * **[FEATURE]** Rudimentary logging of the http requests have been
   implemented.

PRAW 1.0.0
----------
