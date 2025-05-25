.. _refresh_token:

Working with Refresh Tokens
===========================

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
announcements    Access to inbox announcements.
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
modnote          Access mod notes for subreddits I moderate.
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
report           Report content for rules violations. Hide & show individual
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

This script assumes you have configured your application's ``redirect uri`` to
``localhost:8080``

When you execute this script interactively:

1. You will be prompted to provide a comma-separated list of scopes.
2. You will be given a URL that will take you through the auth flow on Reddit.
3. When you open the provided link in your browser, Reddit will ask you for permission
   to grant the application permissions to the scopes requested.
4. After clicking allow, you will have a new authorized application configured.
5. You will be redirected to another page (the application's ``redirect uri``) where
   your refresh token will be displayed and will be printed to the command line.

You only have to run this script once for each refresh token. The refresh token (along
with the application's ``client_id``, ``client_secret``) are valid credentials until
manually revoked by the user.
