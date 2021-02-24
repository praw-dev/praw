.. _refresh_token:

Working with Refresh Tokens
===========================

.. note::

    The process for using refresh tokens is in the process of changing on Reddit's end.
    This documentation has been updated to be aligned with the future of how Reddit
    handles refresh tokens, and will be the only supported method in PRAW 8+. For more
    information please see:
    https://old.reddit.com/r/redditdev/comments/kvzaot/oauth2_api_changes_upcoming/

Reddit OAuth2 Scopes
--------------------

Before working with refresh tokens you should decide which scopes your application
requires. If you want to use all scopes, you can use the special scope ``*``.

To get an up-to-date listing of all Reddit scopes and their descriptions run the
following:

.. code-block:: python

    import requests

    response = requests.get(
        "https://www.reddit.com/api/v1/scopes.json",
        headers={"User-Agent": "fetch-scopes by u/bboe"},
    )

    for scope, data in sorted(response.json().items()):
        print(f"{scope:>18s}  {data['description']}")

As of February 2021, the available scopes are:

================ ======================================================================
Scope            Description
================ ======================================================================
account          Update preferences and related account information. Will not have
                 access to your email or password.
creddits         Spend my reddit gold creddits on giving gold to other users.
edit             Edit and delete my comments and submissions.
flair            Select my subreddit flair. Change link flair on my submissions.
history          Access my voting history and comments or submissions I've saved or
                 hidden.
identity         Access my reddit username and signup date.
livemanage       Manage settings and contributors of live threads I contribute to.
modconfig        Manage the configuration, sidebar, and CSS of subreddits I moderate.
modcontributors  Add/remove users to approved user lists and ban/unban or mute/unmute
                 users from subreddits I moderate.
modflair         Manage and assign flair in subreddits I moderate.
modlog           Access the moderation log in subreddits I moderate.
modmail          Access and manage modmail via mod.reddit.com.
modothers        Invite or remove other moderators from subreddits I moderate.
modposts         Approve, remove, mark nsfw, and distinguish content in subreddits I
                 moderate.
modself          Accept invitations to moderate a subreddit. Remove myself as a
                 moderator or contributor of subreddits I moderate or contribute to.
modtraffic       Access traffic stats in subreddits I moderate.
modwiki          Change editors and visibility of wiki pages in subreddits I moderate.
mysubreddits     Access the list of subreddits I moderate, contribute to, and subscribe
                 to.
privatemessages  Access my inbox and send private messages to other users.
read             Access posts and comments through my account.
report           Report content for rules violations. Hide &amp; show individual
                 submissions.
save             Save and unsave comments and submissions.
structuredstyles Edit structured styles for a subreddit I moderate.
submit           Submit links and comments from my account.
subscribe        Manage my subreddit subscriptions. Manage "friends" - users whose
                 content I follow.
vote             Submit and change my votes on comments and submissions.
wikiedit         Edit wiki pages on my behalf
wikiread         Read wiki pages through my account
================ ======================================================================

Obtaining Refresh Tokens
------------------------

The following program can be used to obtain a refresh token with the desired scopes:

.. literalinclude:: ../examples/obtain_refresh_token.py
    :language: python

.. _using_refresh_tokens:

Using and Updating Refresh Tokens
---------------------------------

Reddit refresh tokens can be used only once. When an authorization is refreshed the
existing refresh token is consumed and a new access token and refresh token will be
issued. While PRAW automatically handles refreshing tokens when needed, it does not
automatically handle the storage of the refresh tokens. However, PRAW provides the
facilities for you to manage your refresh tokens via custom subclasses of
:class:`.BaseTokenManager`. For trivial examples, PRAW provides the
:class:`.FileTokenManager`.

The following program demonstrates how to prepare a file with an initial refresh token,
and configure PRAW to both use that refresh token, and keep the file up-to-date with a
valid refresh token.

.. literalinclude:: ../examples/use_file_token_manager.py
    :language: python

.. _sqlite_token_manager:

SQLiteTokenManager
~~~~~~~~~~~~~~~~~~

For more complex examples, PRAW provides the :class:`.SQLiteTokenManager`.

.. literalinclude:: ../examples/use_sqlite_token_manager.py
    :language: python
