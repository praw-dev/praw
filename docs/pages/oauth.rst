.. _oauth:

PRAW and OAuth
==============

OAuth support allows you to use reddit to authenticate on non-reddit websites.
It also allows a user to authorize an application to perform different groups
of actions on reddit with his account. A moderator can grant an application the
right to set flair on his subreddits without simultaneously granting the
application the right to submit content, vote, remove content or ban people.
Before the moderator would have to grant the application total access, either
by giving it the password or by modding an account controlled by the
applications.

**Note:** Support for OAuth is added in version 2.0. This will not work with
any previous edition.

A step by step OAuth guide
--------------------------

PRAW simplifies the process of using OAuth greatly. The following is a
step-by-step OAuth guide via the interpreter. For real applications you'll
need a webserver, but for educational purposes doing it via the interpreter is
superior. In the next section there is an :ref:`oauth_webserver`.

Step 1: Create an application.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Go to `reddit.com's app page <https://www.reddit.com/prefs/apps/>`_, click on
the "are you a developer? create an app" button. Fill out the name, description
and about url. Name must be filled out, but the rest doesn't. Write whatever
you please. For redirect uri set it to
``http://127.0.0.1:65010/authorize_callback``.  All four variables can be
changed later. Click create app and you should something like the following.

 .. image:: ../_static/CreateApp.png

The random string of letters under your app's name is its ``client id``. The
random string of letters next to secret are your ``client_secret`` and should
not be shared with anybody. At the bottom is the ``redirect_uri``.

Step 2: Setting up PRAW.
^^^^^^^^^^^^^^^^^^^^^^^^

.. WARNING:: This example, like most of the PRAW examples, binds an instance of
  PRAW to the ``r`` variable. While we've made no distinction before, ``r`` (or
  any instance of PRAW) should not be bound to a global variable due to the
  fact that a single instance of PRAW cannot concurrently manage multiple
  distinct user-sessions.

  If you want to persist instances of PRAW across multiple requests in a web
  application, we recommend that you create an new instance per distinct
  authentication. Furthermore, if your web application spawns multiple
  processes, it is highly recommended that you utilize PRAW's
  :ref:`multiprocess <multiprocess>` functionality.

We start as usual by importing the PRAW package and creating a :class:`.Reddit`
object with a clear and descriptive useragent that follows the `api rules
<https://github.com/reddit/reddit/wiki/API>`_.

.. code-block:: pycon

    >>> import praw
    >>> r = praw.Reddit('OAuth testing example by u/_Daimon_ ver 0.1 see '
    ...                 'https://praw.readthedocs.org/en/latest/'
    ...                 'pages/oauth.html for source')

Next we set the app info to match what we got in step 1.

.. code-block:: pycon

    >>> r.set_oauth_app_info(client_id='stJlUSUbPQe5lQ',
    ...                      client_secret='DoNotSHAREWithANYBODY',
    ...                      redirect_uri='http://127.0.0.1:65010/'
    ...                                   'authorize_callback')

The OAuth app info can be automatically set, check out
:ref:`configuration_files` to see how.

Step 3: Getting authorization from the user.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now we need to have a user grant us authorization. We do this by sending them
to a url, where the access we wish to be granted is listed, then they click
'allow' and are redirected to ``redirect_uri`` with a code in the url
parameters that is needed for step 4.

The url we send them to is generated using :meth:`.get_authorize_url`. This
takes 3 parameters. ``state``, which is a string of your choice that represents this
client, ``scope`` which are the reddit scope(s) we ask permission for (see
:ref:`oauth_scopes`) and finally ``refreshable`` which determines whether we
can refresh the access_token (step 6) thus gaining permanent access.

For this tutorial we will need access to the identity scope and be refreshable.

.. code-block:: pycon

    >>> url = r.get_authorize_url('uniqueKey', 'identity', True)
    >>> import webbrowser
    >>> webbrowser.open(url)
    >>> # click allow on the displayed web page

Step 4: Exchanging the code for an access_token and a refresh_token.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After completing step 3, you're redirected to the ``redirect_uri``. Since we
don't have a webserver running there at the moment, we'll see something like
this. Notice the code in the url.

 .. image:: ../_static/CodeUrl.png

Now we simply exchange the code for the access information.

.. code-block:: pycon

    >>> access_information = r.get_access_information('8aunZCxfv8mcCf'
    ...                                               'D8no4CSlO55u0')

This will overwrite any existing authentication and make subsequent requests to
reddit using this authentication unless we set the argument ``update_session``
to ``False``.

:meth:`~.OAuth2Reddit.get_access_information` returns a dict with the
``scope``, ``access_token`` and ``refresh_token`` of the authenticated user. So
later we can swap from one authenticated user to another with

.. code-block:: pycon

    >>> r.set_access_credentials(**access_information)

If ``scope`` contains ``identity`` then ``r.user`` will be set to the
OAuthenticated user with ``r.get_access_information`` or
:meth:`.set_access_credentials` unless we've set the ``update_user`` argument
to ``False``.

Step 5: Use the access.
^^^^^^^^^^^^^^^^^^^^^^^

Now that we've gained access, it's time to use it.

.. code-block:: pycon

    >>> authenticated_user = r.get_me()
    >>> print (authenticated_user.name, authenticated_user.link_karma)

Step 6: Refreshing the access_token.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An access token lasts for 60 minutes. To get access after that period, we'll
need to refresh the access token.

.. code-block:: pycon

    >>> r.refresh_access_information(access_information['refresh_token'])

This returns a dict, where the ``access_token`` key has had its value updated.
Neither ``scope`` nor ``refresh_token`` will have changed.

Note: In version 3.2.0 and higher, PRAW will automatically attempt to refresh
the access token if a refresh token is available when it expires. For most
personal-use scripts, this eliminates the need to use
:meth:`~praw.__init__.AuthenticatedReddit.refresh_access_information` except
when signing in.


.. _oauth_webserver:

An example webserver
--------------------

To run the example webserver, first install flask.

.. code-block:: bash

    $ pip install flask

Then save the code below into a file called example_webserver.py, set the
``CLIENT_ID`` & ``CLIENT_SECRET`` to the correct values and run the program.
Now you have a webserver running on ``http://127.0.0.1:65010`` Go there and
click on one of the links. You'll be asked to authorize your own application,
click allow. Now you'll be redirected back and your user details will be
written to the screen.

.. code-block:: python

    # example_webserver.py #
    ########################

    from flask import Flask, request

    import praw

    app = Flask(__name__)

    CLIENT_ID = 'YOUR_CLIENT_ID'
    CLIENT_SECRET = 'YOUR CLIENT SECRET'
    REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'

    @app.route('/')
    def homepage():
        link_no_refresh = r.get_authorize_url('UniqueKey')
        link_refresh = r.get_authorize_url('DifferentUniqueKey',
                                           refreshable=True)
        link_no_refresh = "<a href=%s>link</a>" % link_no_refresh
        link_refresh = "<a href=%s>link</a>" % link_refresh
        text = "First link. Not refreshable %s</br></br>" % link_no_refresh
        text += "Second link. Refreshable %s</br></br>" % link_refresh
        return text

    @app.route('/authorize_callback')
    def authorized():
        state = request.args.get('state', '')
        code = request.args.get('code', '')
        info = r.get_access_information(code)
        user = r.get_me()
        variables_text = "State=%s, code=%s, info=%s." % (state, code,
                                                          str(info))
        text = 'You are %s and have %u link karma.' % (user.name,
                                                       user.link_karma)
        back_link = "<a href='/'>Try again</a>"
        return variables_text + '</br></br>' + text + '</br></br>' + back_link

    if __name__ == '__main__':
        r = praw.Reddit('OAuth Webserver example by u/_Daimon_ ver 0.1. See '
                        'https://praw.readthedocs.org/en/latest/'
                        'pages/oauth.html for more info.')
        r.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
        app.run(debug=True, port=65010)

.. _oauth_scopes:

OAuth Scopes.
-------------

The following list of access types can be combined in any way you please. Just
pass a string containing each scope that you want (if you want several, they should be seperated by spaces, e.g. ``"identity submit edit"``) to the scope argument of the
``get_authorize_url`` method. The description of each scope is identical to the
one users will see when they have to authorize your application.

+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Type            | Description                                                                                                                        | PRAW methods                                                                                                                                                                                                      |
+=================+====================================================================================================================================+===================================================================================================================================================================================================================+
| creddits        | Spend my reddit gold creddits on giving gold to other users.                                                                       | gild                                                                                                                                                                                                              |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| edit            | Edit and delete my comments and submissions.                                                                                       | edit, delete                                                                                                                                                                                                      |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| flair           | Select my subreddit flair. Change link flair on my submissions.                                                                    | get_flair_choices, select_flair                                                                                                                                                                                   |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| history         | Access my voting history and comments or submissions I've saved or hidden.                                                         | get_hidden, get_saved, get_upvoted, get_downvoted (the last two do not require the ``history`` scope if upvoted and downvoted posts are made public via the preferences). get_comments now also requires history. |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| identity        | Access my reddit username and signup date.                                                                                         | get_me                                                                                                                                                                                                            |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| modconfig       | Manage the configuration, sidebar, and CSS of subreddits I moderate.                                                               | get_settings, set_settings, set_stylesheet, upload_image, create_subreddit, update_settings                                                                                                                       |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| modcontributors | Add/remove users to approved submitter lists and ban/unban users from subreddits I moderate.                                       | add_ban, remove_ban, add_contributor, remove_contributor, add_wiki_contributor, remove_wiki_contributor, add_wiki_ban, remove_wiki_ban (the last four also require the ``modwiki`` scope)                         |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| modflair        | Manage and assign flair in subreddits I moderate.                                                                                  | add_flair_template, clear_flair_template, delete_flair, configure_flair, flair_list, set_flair, set_flair_csv                                                                                                     |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| modlog          | Access the moderation log in subreddits I moderate.                                                                                | get_mod_log                                                                                                                                                                                                       |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| modothers       | Invite or remove other moderators from subreddits I moderate.                                                                      | add_moderator, remove_moderator                                                                                                                                                                                   |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| modposts        | Approve, remove, mark nsfw, and distinguish content in subreddits I moderate.                                                      | approve, distinguish, remove, mark_as_nsfw, unmark_as_nsfw, undistinguish.                                                                                                                                        |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| modself         | Accept invitations to moderate a subreddit. Remove myself as a moderator or contributor of subreddits I moderate or contribute to. | accept_moderator_invite                                                                                                                                                                                           |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| modwiki         | Change editors and visibility of wiki pages in subreddits I moderate.                                                              | add_editor, get_settings (when used on a WikiPage obejct, not a Subreddit object), edit_settings, remove_editor                                                                                                   |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| mysubreddits    | Access the list of subreddits I moderate, contribute to, and subscribe to.                                                         | my_contributions, my_moderation, my_reddits                                                                                                                                                                       |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| privatemessages | Access my inbox and send private messages to other users.                                                                          | mark_as_read, mark_as_unread, send_message, get_inbox, get_modmail, get_sent, get_unread                                                                                                                          |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| read            | Access posts, listings and comments through my account.                                                                            | get_comments, get_new_by_date (and the other listing funcs), get_submission, get_subreddit, get_content, from_url can now access things in private subreddits that the authenticated user has access to.          |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| report          | Report content for rules violations. Hide & show individual submissions.                                                           | report, hide, unhide                                                                                                                                                                                              |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| save            | Save and unsave comments and submissions.                                                                                          | save, unsave                                                                                                                                                                                                      |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| submit          | Submit links and comments from my account.                                                                                         | add_comment, reply, submit                                                                                                                                                                                        |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| subscribe       | Manage my subreddit subscriptions.                                                                                                 | subscribe, unsubscribe                                                                                                                                                                                            |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| vote            | Submit and change my votes on comments and submissions.                                                                            | clear_vote, upvote, downvote, vote                                                                                                                                                                                |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| wikiedit        | Edit wiki pages on my behalf                                                                                                       | edit_wiki_page                                                                                                                                                                                                    |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| wikiread        | Read wiki pages through my account.                                                                                                | get_wiki_page, get_wiki_pages                                                                                                                                                                                     |
+-----------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
