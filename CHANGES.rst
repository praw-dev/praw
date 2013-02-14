Changelog
=========

This is the changelog for the released versions of PRAW. These changes are
divided into four categories.

 * **[FEATURE]** Something new has been added.
 * **[BUGFIX]** Something was broken before, but now is fixed.
 * **[REDDIT]** A change caused by an upstream change from Reddit.
 * **[CHANGE]** Other changes affecting user programs, such as the renaming of
   a function.

Read `r/changelog <http://www.reddit.com/r/changelog>`_ to be notified of
upstream changes.

PRAW 2.0.10
-----------

 * **[FEATURE]** Add ``delete_flair`` method to ``Submission`` and ``Reddit``
   objects.

PRAW 2.0.9
----------

 * **[FEATURE]** Add parameter ``update_user`` (default False) to
   ``get_unread`` if it and ``unset_has_mail`` are both True, then the ``user``
   object in the ``reddit`` object will have it's ``has_mail`` attribute set to
   ``False``.
 * **[FEATURE]** Add ``get_friends`` and ``get_blocked`` to
   ``LoggedInRedditor``.
 * **[FEATURE]** Add the *read* scope to ``get_all_comments`` in the ``Reddit``
   object.
 * **[FEATURE]** Add the *read* scope to ``get_comments`` and the subreddit
   listings such as ``get_new`` in the ``Reddit`` and ``Subreddit`` object.
 * **[BUGFIX]** Fix bug in ``MoreComments.comments``.
 * **[CHANGE]** Break ``get_friends`` and ``get_banned`` until there is an
   upstream fix to mean that does not require ssl for those endpoints.

PRAW 2.0.8
----------

 * **[FEATURE]** Add ``unset_has_mail`` parameter to ``get_unread``, if it's
   set to ``True``, then it will set ``has_mail`` for the logged-in user to
   ``False``.

PRAW 2.0.7
----------

 * **[REDDIT]** A `reddit update <`http://redd.it/17oer0>`_ broke PRAW's
   ability to use ``login`` if it was authenticated as a logged-in user. This
   update adds the ability to re-login.
 * **[CHANGE]** ``get_flair_list`` can now be used when logged-in as a regular
   user, being logged in as a mod of the subreddit is no longer required.

PRAW 2.0.6
----------

 * **[FEATURE]** Add the ``get_unmoderated`` method to ``Subreddit`` and base
   reddit objects. This returns a listings of submissions that haven't been
   approved/removed by a moderator.


PRAW 2.0.5
----------

 * **[FEATURE]** Add the parameter ``gilded_only`` to ``get_comments`` and
   ``get_all_comments`` methods in ``Subreddit`` and base reddit objects. If
   ``gilded_only`` is set to ``True``, then only gilded comments will be
   returned.
 * **[FEATURE]** Add ``get_comments`` method to Reddit object. It works like
   ``get_comments`` in Subreddit objects except it takes the subreddit as the
   first argument.

PRAW 2.0.4
----------

 * **[BUGFIX]** Fix python 3 failure introduced in 2.0.3 within the test suite.

PRAW 2.0.3
----------

 * **[FEATURE]** Add ``delete_image`` method to Subreddit objects (also
   callable on the base reddit object with the subreddit as the first
   argument):
 * **[CHANGE]** PRAW now requires version 0.4 of ``update_checker``.

PRAW 2.0.2
----------

 * **[BUGFIX]** Fixed bug when comparing MoreComments classes in Python 3.x

PRAW 2.0.1
----------

 * **[BUGFIX]** Fix bug with ``limit=None`` in method ``replace_more_comments``
   in ``Submission`` object.

PRAW 2.0.0
----------

 * **[FEATURE]** Support reddit OAuth2 scopes (passwordless authentication).
   See :ref:`oauth` for usage information.
 * **[FEATURE]** Maximize the number of items fetched when explicit limits are
   set thus reducing the number of requests up to 4x in some cases.
 * **[FEATURE]** Add the following API methods to Subreddit objects (also
   callable on the base reddit object with the subreddit as the first
   argument):
    * ``accept_moderator_invite`` -- accept a pending moderator invite
    * ``get_mod_log``  -- return ModAction objects for each item (run
      vars(item), to see available attributes)
    * ``configure_flair``  -- interface to subreddit flair options
    * ``upload_image`` -- upload an image for the subreddit header or use in
      CSS
 * **[FEATURE]** Support 'admin' distinguishing of items via ``distinguish``
 * **[FEATURE]** Ability to specify max-character limit for object-to-string
   representations via ``output_chars_limit`` in ``praw.ini``
 * **[CHANGE]** Remove ``comments_flat`` property of Submission objects. The
   new ``praw.helpers.flatten_tree`` can be used to flatten comment trees.
 * **[CHANGE]** Remove ``all_comments`` and ``all_comments_flat`` properties of
   Submission objects. The now public method ``replace_more_comments`` must now
   be explicitly called to replace instances of ``MoreComments`` within the
   comment tree.
 * **[CHANGE]** The ``content_id`` attribute of ``RedditContentObject`` has
   been renamed to ``fullname``
 * **[CHANGE]** The ``info`` base Reddit instance method has been renamed to
   ``get_info``.
 * **[CHANGE]** ``get_saved_links`` has been renamed to ``get_saved`` and moved
   to the ``LoggedInRedditor`` (``r.user``) namespace.
 * **[CHANGE]** The Subreddit ``get_info`` method has been renamed to
   ``from_url`` and supports parameters for changing the number of comments to
   fetch and by what sort method.
 * **[CHANGE]** The ``get_submission`` method also now supports parameters for
   changing the number of comments to fetch and by what sort method.
 * **[CHANGE]** ``(un)mark_as_nsfw`` can no longer be used on Subreddit
   objects. Use ``update_settings(nsfw=True)`` instead.
 * **[CHANGE]** Remove depreciated method ``compose_message``.
 * **[CHANGE]** Refactored and add a number of exception classes (`docs
   <https://python-reddit-api-wrapper.readthedocs.org/en/latest/
   praw.html#module-praw.errors>`_,
   `source <https://github.com/praw-dev/praw/blob/master/praw/errors.py>`_)
   This includes the renaming of:
    * ``BadCaptcha`` to ``InvalidCaptcha``
    * ``NonExistantUser`` to ``InvalidUser``
 * **[CHANGE]** Simplify content-limit handling and remove the following
   no-longer necessary parameters from ``praw.ini``:
    * ``comment_limit``
    * ``comment_sort``
    * ``default_content_limit``
    * ``gold_comments_max``
    * ``more_comments_max``
    * ``regular_comments_max``
 * **[CHANGE]** Move the following methods from ``LoggedInRedditor`` to base
   reddit object.
    * ``get_unread``
    * ``get_inbox``
    * ``get_mod_mail``
    * ``get_sent``

PRAW 1.0.16
-----------

 * **[FEATURE]** Add support for r/random

PRAW 1.0.15
-----------

 * **[FEATURE]** Added the functions ``hide`` and ``unhide`` to ``Submission``.
 * **[FEATURE]** Added function ``is_username_available`` to ``Reddit``.

PRAW 1.0.14
-----------

 * **[FEATURE]** Extended functionality to Python 3.3

PRAW 1.0.13
-----------

 * **[BUGFIX]** Fixed non-equality bug. Before comparing two PRAW objects with
   != would always return ``True``.
 * **[FEATURE]** Added the function ``my_contributions`` to
   ``LoggedInRedditor``.  Use this to find the subreddits where the user is an
   approved contributor.
 * **[CHANGE]** Voting on something will now force the next call to
   ``get_liked`` or ``get_disliked`` to re-query from the reddit rather than
   use the cache.

PRAW 1.0.12
-----------

 * **[FEATURE]** Support for optional 'prev' values added.

PRAW 1.0.11
-----------

 * **[FEATURE]** Added ``get_top`` to ``Reddit``.

PRAW 1.0.10
-----------

 * **[FEATURE]** Allow for the OS to not be identified when searching for
   ``praw.ini``.

PRAW 1.0.9
----------

 * **[FEATURE]** Added the functions ``mark_as_NSFW`` and ``unmark_as_NSFW`` to
   ``Submission`` and ``Subreddit`` .

PRAW 1.0.8
----------

 * **[CHANGE]** Printing a ``Submission`` to ``sys.stdout`` will now limit the
   output length to 80 chars, just like ``Comment`` does.
 * **[FEATURE]** The maximum amount of comments that can be retrieved alongside
   a submission for gold and regular accounts has been exported to
   ``praw.ini``.
 * **[REDDIT]** Checks for login/moderator in ``get_moderator`` and
   ``get_flair`` for Subreddit are no longer necessary.
 * **[FEATURE]** Added the function ``refresh``to ``Submission``, ``Subreddit``
   and ``Redditor``. This will make PRAW re-query either the Reddit or the
   cache, depending on whether the last call was within ``cache_timeout``, for
   the latest values and update the objects values.
 * **[FEATURE]** Added functions ``get_liked``, ``get_disliked`` and
   ``get_hidden`` to LoggedInRedditor to allow you to get the Things the user
   has upvoted, downvoted or hidden.
 * **[BUGFIX]** Temporary bugfix until prevstyles become optional.
 * **[FEATURE]** Added prevstyle to set_stylesheet requests.
 * **[BUGFIX]** Putting in ``user`` or ``pswd`` to ``praw.ini`` without values
   will no longer make it impossible to login.
 * **[FEAUTRE]** You can now have just ``user`` filled out in ``praw.ini`` to
   ease login while remaining safe.

PRAW 1.0.7
----------

 * **[REDDIT]** New fields ``prev_description_id`` and
   ``prev_public_description_id`` added to ``set_settings`` as per the upstream
   change

PRAW 1.0.6
----------

 * **[CHANGE]** ``compose_message`` has been renamed to ``send_message`` in
   ``Reddit`` and ``LoggedInRedditor``. ``compose_message`` is now depreciated
   and will be removed around the end of 2012.

PRAW 1.0.5
----------

 * **[FEATURE]** ``get_popular_reddits`` added to ``Reddit``.

PRAW 1.0.4
----------

 * **[FEATURE]** Added ``get_new`` and ``get_controversial`` to ``Reddit``.

PRAW 1.0.3
----------

 * **[REDDIT]** The logged in / moderator checks for ``flair_list`` in
   ``Reddit`` are no longer needed and have been removed.

PRAW 1.0.2
----------

 * **[FEATURE]** ``score`` property wrapped function have been added to
   ``Comment``.

PRAW 1.0.1
----------

 * **[FEATURE]** ``require_moderator`` decorator now supports multi-reddits.
 * **[FEATURE]** Rudimentary logging of the http requests have been
   implemented.

PRAW 1.0.0
----------
