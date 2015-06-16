.. begin_changelog_intro

Changelog
=========

The changes listed below are divided into four categories.
 * **[BUGFIX]** Something was broken before, but is now fixed.
 * **[CHANGE]** Other changes affecting user programs, such as the renaming of
   a function.
 * **[FEATURE]** Something new has been added.
 * **[REDDIT]** A change caused by an upstream change from reddit.

Read `/r/changelog <http://www.reddit.com/r/changelog>`_ to be notified of
upstream changes.

.. end_changelog_intro

Visit `the changelog on ReadTheDocs
<http://praw.readthedocs.org/en/latest/pages/changelog.html>`_ for properly
formatted links that link to the relevant place in the code overview.

.. begin_changelog_body

PRAW 3.0.0
----------
 * **[CHANGE]** All requests should now be through HTTPS.
 * **[CHANGE]** All exceptions should be in the PRAW namespace. In particular,
   there should be no more exceptions under the ``requests`` namespace.
 * **[CHANGE]** All previously deprecated methods have been removed.
 * **[CHANGE]** The ``display_name`` attribute on instances of
   :class:`Subreddit` is now lazily loaded and will match the casing on the
   site, not the casing used to construct the Subreddit instance. To quickly
   fetch the name of an unloaded Subreddit, use ``str(sub_instance)``, or
   ``unicode(sub_instance)``.
 * **[CHANGE]** Removed :class:`praw.Config` instance attribute ``is_reddit``.
 * **[CHANGE]** :meth:`~praw.__init__.BaseReddit.evict` now returns the number
   of items evicted.
 * **[CHANGE]** Removed ``praw.ini`` parameter ``decode_html_entities``.
   Entities, e.g., ``&``, ``<`` ``>``, are now always decoded.
 * **[FEATURE]** Added :meth:`get_message` to fetch a single Message object
   by its ID.
 * **[FEATURE]** Added :meth:`get_sticky` to get a Subreddit's sticky post.
 * **[FEATURE]** Refresh tokens can be specified in ``praw.ini`` via
   ``oauth_refresh_token``.
 * **[FEATURE]** Added :meth:`create_multireddit` to create a new Multireddit.
 * **[FEATURE]** Added :meth:`copy_multireddit` to copy a Multireddit.
 * **[FEATURE]** Added :meth:`edit_multireddit` to edit an existing
   Multireddit.
 * **[FEATURE]** Added :meth:`get_multireddits` to get a list of Multireddits
   belonging to the requested user.
 * **[FEATURE]** Added :meth:`rename_multireddit` to rename an existing
   Multireddit.
 * **[FEATURE]** Added :meth:`set_suggested_sort` to change a submission's sort
   order.
 * **[FEATURE]** Added ``method`` as optional parameter to
   :meth:`request_json`, so that a request method other than 'POST' can be
   specified.
 * **[FEATURE]** Added :meth:`praw.__init__.ReportMixin.hide` and
   :meth:`praw.__init__.ReportMixin.unhide`, which accept up to 50 fullnames to
   be hidden at one time. The appropriate methods in :class:`objects.Hideable`
   now point here instead.
 * **[FEATURE]** Added :meth:`add_editor`, :meth:`remove_editor`,
   :meth:`get_settings` and :meth:`edit_settings` to :class:`WikiPage`
   for managing editors and permission levels of individual wiki pages.
 * **[REDDIT]** Removed ``send_feedback`` as it is no longer supported by
   reddit.
 * **[REDDIT]** Added ``DeprecationWarning`` to :meth:`login` as reddit will
   stop supporting cookie-based authentication on 2015/08/03.

PRAW 2.1.21
-----------
 * **[BUGFIX]** Fix assertion error in :meth:`.replace_more_comments` with
   continue this thread links that have more than one child.
 * **[BUGFIX]** :meth:`.refresh` on :class:`praw.objects.Submission` no longer
   loses comment sort order and other manually specified parameters.
 * **[REDDIT]** Add ``hide_ads`` as a parameter to
   :meth:`~praw.__init__.ModConfigMixin.set_settings`.
 * **[REDDIT]** :meth:`.create_redditor` no longer requires a captcha
 * **[REDDIT]** :meth:`.create_subreddit` may require a captcha

PRAW 2.1.20
-----------
 * **[BUGFIX]** Attempting to lazyload an attribute of a comment that has been
   removed will explicitly raise a :meth:`praw.errors.InvalidComment`
   exception, rather than an ``IndexError`` (issue #339).
 * **[BUGFIX]** :meth:`.replace_more_comments` handles `continue this thread`
   type ``MoreComments`` objects.
 * **[FEATURE]** Added :meth:`praw.helpers.valid_redditors`.
 * **[FEATURE]** Added a ``nsfw`` parameter to :meth:`.get_random_subreddit`
   that permits fetching a random NSFW Subreddit. This change also supports
   fetching these subreddits via ``get_subreddit('randnsfw')``.
 * **[FEATURE]** Added a ``from_sr`` parameter to
   :meth:`~.PrivateMessagesMixin.send_message` to send the private message from
   a subreddit you moderate (Like the "From" dropdown box when composing a
   message).
 * **[FEATURE]** Added :class:`Multireddit`
 * **[FEATURE]** Added :meth:`get_multireddit` to get a single multireddit obj
 * **[FEATURE]** Added :meth:`get_my_multireddits` to get all multireddits
   owned by the logged in user.
 * **[FEATURE]** Added :meth:`get_multireddit` to :class:`Redditor` to quickly
   get a multireddit belonging to that user.
 * **[FEATURE]** :class:`praw.objects.Comment`,
   :class:`praw.objects.Redditor`, and :class:`praw.objects.Submission` are now
   gildable.
 * **[FEATURE]** :class:`praw.objects.Comment` is now saveable.
 * **[REDDIT]** Handle upstream change in reddit's OAuth2 scope parsing.

PRAW 2.1.19
-----------
 * **[BUGFIX]** Support URLs in
   :meth:`~praw.__init__.UnauthenticatedReddit.search`.
 * **[BUGFIX]** Fix bug where ``json_dict`` was set to ``None`` when it should
   not have been.
 * **[BUGFIX]** Fix :meth:`.get_subreddit_recommendations` to work with the
   updated API route.
 * **[BUGFIX]** Track time between requests using ``timeit.default_timer``.
 * **[CHANGE]** :meth:`.get_friends` and :meth:`~.Subreddit.get_banned` once
   again work.
 * **[CHANGE]** :meth:`.is_root` no longer requires fetching submission
   objects.
 * **[REDDIT]** Support ``thing_id`` lists in :meth:`.get_info`.
 * **[FEATURE]** Support providing HTTPS proxies, that is, proxies specific to
   handling HTTPS requests.
 * **[FEATURE]** :meth:`~praw.objects.Redditor.get_liked` and
   :meth:`~praw.objects.Redditor.get_disliked` now accept additional
   arguments, e.g., limit.
 * **[FEATURE]** Add :meth:`.get_messages` for specifically retreiving messages
   (not replies).
 * **[REDDIT]** Add ``collapse_deleted_comments`` as a parameter to
   :meth:`~praw.__init__.ModConfigMixin.set_settings`.
 * **[REDDIT]** :meth:`~praw.__init__.ModOnlyMixin.get_stylesheet` now supports
   using the ``modconfg`` OAuth scope.
 * **[REDDIT]** :meth:`~praw.__init__.ModOnlyMixin.get_stylesheet` no longer
   accepts the ``prevstyle`` argument.


PRAW 2.1.18
-----------
 * **[FEATURE]** Add the :meth:`~praw.objects.Subreddit.get_flair_choices`
   method to the :class:`.Submission` class, which returns the choices for user
   flair in the subreddit and the current flair of the authenticated user.
 * **[FEATURE]** Add the :meth:`~praw.objects.Submission.get_flair_choices`
   method to the :class:`.Submission` class, which returns the choices for
   link flair on this submission as well as it's current flair.
 * **[BUGFIX]** Fix python3 issue with ``func_defaults``.
 * **[REDDIT]** Avoid exceptions caused by upstream changes by reddit with
   respect to conflicts between json attributes and
   :class:`.RedditContentObject` properties. In such cases, the attribute from
   reddit will be suffixed with "_reddit".

PRAW 2.1.17
-----------
 * **[BUGFIX]** Remove the built-in ``score`` property from comments as reddit
   provides that attribute as of 2014/06/18.
 * **[FEATURE]** :meth:`~praw.__init__.SubmitMixin.submit` now supports
   a ``resubmit`` argument to allow the submission of an already submitted url.

PRAW 2.1.16
-----------
 * **[BUGFIX]** Fix incorrect username when building Redditor objects from
   wikipage submissions.
 * **[CHANGE]** Increase the dependency of ``update_checker`` to 0.10 or later
   to prevent ImportWarnings (issue 291).
 * **[CHANGE]** :meth:`~.Subreddit.get_banned` now takes a ``user_only``
   argument (default: ``True``). When the value is explicitly passed as
   ``False`` the return value is not a generator of ``Redditor`` objects, but a
   generator of dictionaries whose ``name`` key corresponds to the ``Redditor``
   object and whose ban-note is at key ``note``.
 * **[FEATURE]** Enable gathering of duplicate submissions for a Submission
   object (issue 290).
 * **[FEATURE]** Add :meth:`praw.__init__.AuthenticatedReddit.delete`.

PRAW 2.1.15
-----------
 * **[FEATURE]** Add ``save`` OAuth scope to
   :meth:`~praw.objects.Saveable.save` and
   :meth:`~praw.objects.Saveable.unsave`.
 * **[BUGFIX]** Fix Google AppEngine bug with ``platform.platform``.
 * **[REDDIT]** Using :meth:`~praw.__init__.UnauthenticatedReddit.get_flair`
   now requires moderator access. See `this /r/redditdev thread
   <http://www.reddit.com/r/redditdev/comments/1xreor/
   has_there_been_a_change_to_the_permissions/>`_
 * **[CHANGE]** Increase the dependency of ``update_checker`` to 0.9 or later.

PRAW 2.1.14
-----------
 * **[CHANGE]** Increase the dependency of ``six`` to 1.4 or later.

PRAW 2.1.13
-----------
 * **[FEATURE]** Support building wheel binary distributions.
 * **[FEATURE]** :meth:`~praw.__init__.UnauthenticatedReddit.get_submission`
   and :meth:`~praw.objects.Submission.from_url` now supports url parameters.
   Both included within the url and explicitly via the "params" argument.
 * **[CHANGE]** The dependency on ``update_checker`` has been increased
   to >= 0.8.
 * **[REDDIT]** Add support for changes to UserLists on reddit.
 * **[REDDIT]** Using get_flair_list now requires moderator access. See `this
   /r/redditdev thread <http://www.reddit.com/r/redditdev/comments/1xreor/
   has_there_been_a_change_to_the_permissions/>`_
 * **[BUGFIX]** Fix configuration parsing for ``store_json_result``.
 * **[BUGFIX]** Fix duplicate bug in :class:`.BoundedSet`.

PRAW 2.1.12
-----------
 * **[FEATURE]** Add :attr:`.json_dict` to :class:`.RedditContentObject`.
 * **[FEATURE]** You can now give configuration settings directly when
   instantiating a :class:`.BaseReddit` object. See `the configuration files
   <https://praw.readthedocs.org/en/latest/pages/configuration_files.html>`_
 * **[BUGFIX]** Fixed a bug that caused an ``AttributeError`` to be raised when
   using a deprecated method.

PRAW 2.1.11
-----------
 * **[FEATURE]** Added :meth:`~praw.objects.Moderatable.ignore_reports` and
   :meth:`~praw.objects.Moderatable.unignore_reports` to :class:`.Comment` and
   :class:`.Submission`.
 * **[BUGFIX]** The ``history`` scope is not required for
   :meth:`~praw.objects.Redditor.get_comments`, :meth:`.get_overview` and
   :meth:`.get_submitted` despite the official `reddit documentation
   <https://www.reddit.com/dev/api#GET_user_{username}_submitted>`_ saying so.
   Redditors may choose to make their voting record public, in which case no
   authentication is required for :meth:`.get_disliked` or :meth:`.get_liked`.
   The ``history`` scope requirement for the above-mentioned methods has been
   removed.

PRAW 2.1.10
-----------
 * **[FEATURE]** Add :meth:`.get_new_subreddits` to return the newest
   subreddits.
 * **[FEATURE]** Add the arguments ``save`` and ``send_replies`` to
   :meth:`~praw.__init__.SubmitMixin.submit`.
 * **[FEATURE]** Create and add ``history`` scope to
   :meth:`~praw.objects.Redditor.get_comments`, :meth:`.get_disliked`,
   :meth:`.get_liked`, :meth:`.get_overview`, :meth:`.get_submitted`,
   :meth:`.get_hidden` and :meth:`.get_saved`.

PRAW 2.1.9
----------
 * **[FEATURE]** :meth:`mark_as_nsfw` and :meth:`unmark_as_nsfw` can now be
   used if the currently authenticated user is the author of the Submission.
 * **[FEATURE]** :meth:`~.ModOnlyMixin.get_contributors` can now be used for
   accessing the contributor list of protected/private subreddits without
   requiring moderator access. See issue `issue 246
   <https://github.com/praw-dev/praw/issues/246>`_.
 * **[BUGFIX]** Fixed :class:`.Comment` erroneously having the methods
   ``mark_as_nsfw`` and ``unmark_as_nsfw``, despite comments not being able to
   be marked as NSFW.
 * **[REDDIT]** Update :meth:`.get_subreddit_recommendations` to handle changed
   returned data format.

PRAW 2.1.8
----------
 * **[FEATURE]** Add :meth:`.get_subreddit_recommendations` to get a
   recommendation of subreddits based on a list of provided subreddits.
 * **[FEATURE]** :class:`.Subreddit` now has an ``__repr__`` method. So it's
   now possible to identify what subreddit the object represents from the human
   readable representation of the object.
 * **[FEATURE]** Add :meth:`praw.__init__.UnauthenticatedReddit.get_rising`
   that returns the rising listing of the front page in the context of the
   currently logged-in user (if any).

PRAW 2.1.7
----------
 * **[FEATURE]** Add methods :meth:`.set_contest_mode` and
   :meth:`.unset_contest_mode` to :class:`.Submission`, for (un)setting of
   contest modes. See `this Reddit post
   <http://www.reddit.com/r/bestof2012/comments/159bww/
   introducing_contest_mode_a_tool_for_your_voting/>`_
   for information about contest mode.
 * **[FEATURE]** Move methods :meth:`.get_liked` and :meth:`.get_liked` to
   :class:`.Redditor` from :class:`.LoggedInRedditor`. Redditors can make their
   likes and dislikes public. Having :meth:`.get_liked` and :meth:`.get_liked`
   on :class:`.Redditor` allows PRAW to access this info.
 * **[FEATURE]** The ``has_fetched`` attribute has been added to all objects
   save :class:`.Reddit`, see the `lazy loading
   <http://praw.readthedocs.org/en/latest/pages/lazy-loading.html>`_ page in
   PRAW's documentation for more details.
 * **[BUGFIX]** Fixed a bug that caused the ``timeout`` configuration setting
   to always be the default 45 irrespective of what it was set to in
   ``praw.ini``.

PRAW 2.1.6
----------

 * **[BUGFIX]** PRAW automatically retries failed requests to reddit if the
   error is likely to be a temporary one. This resulted in spamming reddit if
   the error occurred after content had been saved to reddit's database.
   Therefore the following methods will no longer retry failed request
   :meth:`~praw.__init__.ModConfigMixin.upload_image`,
   :meth:`~praw.__init__.PrivateMessagesMixin.send_message`,
   :meth:`~praw.__init__.SubmitMixin.submit`,
   :meth:`~praw.__init__.UnauthenticatedReddit.send_feedback`,
   :meth:`~praw.objects.Inboxable.reply` and
   :meth:`~praw.objects.Submission.add_comment`.
   Additionally :meth:`~praw.__init__.BaseReddit.request_json` now has the
   ``retry_on_error`` argument, which if set to ``True`` will prevent retries
   of the request if it fails.

PRAW 2.1.5
----------

 * **[FEATURE]** :meth:`~praw.__init__.AuthenticatedReddit.select_flair` method
   added, can be used to change your flair without moderator access on
   subreddits that allow it.
 * **[FEATURE]** Add :meth:`~praw.objects.Submission.sticky` and
   :meth:`~praw.objects.Submission.unsticky` to sticky and unsticky a
   submission to the top of a subreddit.
 * **[FEATURE]** Add arguments syntax and period to
   :meth:`~praw.__init__.UnauthenticatedReddit.search`.
 * **[FEATURE]** PRAW will now try to use the http_proxy environment variable
   for proxy settings, if no proxy is set in the configuration file.
 * **[BUGFIX]** :meth:`~praw.__init__.ModOnlyMixin.get_stylesheet` erroneously
   required moderator access. It now just requires that the authenticated user
   has access to the subreddit.
 * **[BUGFIX]** Fix bug that prevented the usage of
   :meth:`~praw.objects.Subreddit.search` when called from :obj:`.Subreddit`.

PRAW 2.1.4
----------

 * **[FEATURE]** :meth:`~praw.__init__.ModOnlyMixin.get_mod_mail` can now be
   used to get moderator mail from individual subreddits, instead of all
   moderated subreddits, just like
   :meth:`~praw.__init__.ModOnlyMixin.get_mod_queue`.
 * **[FEATURE]** Added :meth:`~.get_mentions` which is a :meth:`.get_content`
   generator for username mentions. Only usable if the authenticated user has
   gold.
 * **[BUGFIX]** Fixed an error in
   :meth:`~praw.__init__.ModOnlyMixin.get_mod_queue`,
   :meth:`~praw.__init__.ModOnlyMixin.get_reports`,
   :meth:`~praw.__init__.ModOnlyMixin.get_spam` and
   :meth:`~praw.__init__.ModOnlyMixin.get_unmoderated` when calling them from
   :obj:`.Reddit` without giving the subreddit argument explicitly.
 * **[REDDIT]** New fields ``public_traffic`` added to
   :meth:`~praw.__init__.ModConfigMixin.set_settings` as per the upstream
   change.

PRAW 2.1.3
----------

 * **[FEATURE]** Added :meth:`.UnauthenticatedReddit.get_random_submission`.
 * **[BUGFIX]** Verify that ``sys.stdin`` has ``closed`` attribute before
   checking if the stream is closed.

PRAW 2.1.2
----------

 * **[BUGFIX]** Avoid occasionally processing duplicates in
   :meth:`~praw.helpers.comment_stream`.
 * **[CHANGE]** :meth:`~praw.helpers.comment_stream` yields comments in a
   consitent order (oldest to newest).
 * **[FEATURE]** Support fetching submission listings for domains via
   :meth:`.get_domain_listing`.

PRAW 2.1.1
----------

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
   https://github.com/praw-dev/praw/issues/213.
 * **[BUGFIX]** Fix a python 3.3 bug in
   :meth:`~.Subreddit.upload_image`. See
   https://github.com/praw-dev/praw/issues/211.

PRAW 2.0.15
-----------

 * **[FEATURE]** PRAW can now use a proxy server, see `#206
   <https://github.com/praw-dev/praw/pull/206>`_. The parameter
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
   WikiPage.
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
   :meth:`.praw.objects.Subreddit.get_rising` method instead of the old
   :meth:`.get_new_by_rising` and :meth:`~.Subreddit.get_new` instead of
   :meth:`.get_new_by_date`.
 * **[CHANGE]** The dependency on ``update_checker`` has been increased from >=
   0.4 to >= 0.5.
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
   ``user`` object in the :class:`.Reddit` object will have its ``has_mail``
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

 * **[REDDIT]** A `reddit update
   <http://www.reddit.com/r/redditdev/comments/17oer0/api_change_login_requests_containing_a_session/>`_
   broke PRAW's ability to use :meth:`.login` if it was authenticated as a
   logged-in user.  This update adds the ability to re-login.
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
   the subreddit as the first argument).
 * **[CHANGE]** PRAW now requires version 0.4 of ``update_checker``.

PRAW 2.0.2
----------

 * **[BUGFIX]** Fixed bug when comparing :class:`.MoreComments` classes in
   Python 3.x.

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
     invite.
   * :meth:`~.Subreddit.get_mod_log`  -- return ModAction objects for each item
     (run vars(item), to see available attributes).
   * :meth:`~.Subreddit.configure_flair`  -- interface to subreddit flair
     options.
   * :meth:`~.Subreddit.upload_image` -- upload an image for the subreddit
     header or use in CSS.

 * **[FEATURE]** Support 'admin' and `special` distinguishing of items via
   :meth:`.distinguish`.
 * **[FEATURE]** Ability to specify max-character limit for object-to-string
   representations via ``output_chars_limit`` in ``praw.ini``.
 * **[CHANGE]** Remove ``comments_flat`` property of :class:`.Submission`
   objects. The new :meth:`praw.helpers.flatten_tree` can be used to flatten
   comment trees.
 * **[CHANGE]** Remove ``all_comments`` and ``all_comments_flat`` properties of
   Submission objects. The now public method :meth:`.replace_more_comments`
   must now be explicitly called to replace instances of :class:`.MoreComments`
   within the comment tree.
 * **[CHANGE]** The ``content_id`` attribute of :class:`.RedditContentObject`
   has been renamed to :attr:`.fullname`.
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
   <https://praw.readthedocs.org/en/latest/pages/code_overview.html#module-praw.errors>`_,
   `source <https://github.com/praw-dev/praw/blob/master/praw/errors.py>`_)
   This includes the renaming of:

   * ``BadCaptcha`` to :exc:`.InvalidCaptcha`.
   * ``NonExistantUser`` to :exc:`.InvalidUser`.

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
   * :meth:`~praw.__init__.ModOnlyMixin.get_mod_mail`
   * :meth:`.get_sent`

PRAW 1.0.16
-----------

 * **[FEATURE]** Add support for /r/random.

PRAW 1.0.15
-----------

 * **[FEATURE]** Added the functions :meth:`~praw.objects.Hideable` and
   :meth:`~praw.objects.Hideable.unhide` to :class:`.Submission`.
 * **[FEATURE]** Added function :meth:`.is_username_available` to
   :class:`.Reddit`.

PRAW 1.0.14
-----------

 * **[FEATURE]** Extended functionality to Python 3.3.

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
   ``prev_public_description_id`` added to
   :meth:`~praw.__init__.ModConfigMixin.set_settings` as per the upstream
   change.

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

.. end_changelog_body
