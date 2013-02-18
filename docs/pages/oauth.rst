.. _oauth:

PRAW and OAuth
==============

OAuth support allows you to use Reddit to authenticate on non-Reddit websites.
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

Go to `reddit.com's app page <https://ssl.reddit.com/prefs/apps/>`_, click on
the "are you a developer? create an app" button. Fill out the name, description
and about url. Name must be filled out, but the rest doesn't. Write whatever
you please. For redirect url set it to
http://127.0.0.1:65010/authorize_callback.  All four variables can be changed
later. Click create app and you should something like the following.

 .. image:: ../_static/CreateApp.png

The random string of letters under your app's name is it's ``client id``. The
random string of letters next to secret are your ``client_secret`` and should
not be shared with anybody. At the bottom is the ``redirect_url``.

Step 2: Setting up PRAW.
^^^^^^^^^^^^^^^^^^^^^^^^

We start as usual by importing the PRAW package and creating a ``Reddit``
object with a clear and descriptive useragent that follows the `api rules
<https://github.com/reddit/reddit/wiki/API>`_.

.. code-block:: pycon

    >>> import praw
    >>> r = praw.Reddit('OAuth testing example by u/_Daimon_ ver 0.1 see '
    ...                 'github.com/praw-dev/praw/wiki/OAuth for source')

Next we set the app info to match what we got in step 1.

.. code-block:: pycon

    >>> r.set_oauth_app_info(client_id='stJlUSUbPQe5lQ',
    ...                      client_secret='DoNotSHAREWithANYBODY',
    ...                      redirect_url='http://127.0.0.1:65010/'
    ...                                   'authorize_callback')

The OAuth app info can be automatically set, check out
:ref:`configuration_files` to see how.

Step 3: Getting authorization from the user.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now we need to have a user grant us authorization. We do this by sending them
to a url, where the access we wish to be granted is listed, then they click
'allow' and are redirected to ``redirect_url`` with a code in the url
parameters that is needed for step 4.

The url we send them to is generated using ``r.get_authorize_url``. This takes
3 parameters. ``state``, which is a unique key that represent this client,
``scope`` which are the reddit scope we ask permission for (see
:ref:`oauth_scopes`) and finally ``refreshable`` which determines whether we
can refresh the access_token (step 6) thus gaining permanent access.

For this tutorial we will need access to the identity scope and be refreshable. 

.. code-block:: pycon

    >>> url = r.get_authorize_url('uniqueKey', 'identity', True)
    >>> import webbrowser
    >>> webbrowser.open(url)
    >>> # click allow on the webend

Step 4: Exchanging the code for an access_token and a refresh_token.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After completing step 3, you're redirected to the ``redirect_url``. Since we
don't have a webserver running there at the moment, we'll see something like
this. Notice the code in the url.

 .. image:: ../_static/CreateApp.png

Now we simply exchange the code for the access information.

.. code-block:: pycon

    >>> access_information = r.get_access_information('8aunZCxfv8mcCf'
    ...                                               'D8no4CSlO55u0')

This will overwrite any existing authentication and make subsequent requests to
reddit using this authentication unless we set the argument ``update_session``
to ``False``.

``get_access_information`` returns a dict with the ``scope``, ``access_token``
and ``refresh_token`` of the authenticated user. So later we can swap from one
authenticated user to another with

.. code-block:: pycon

    >>> r.set_access_credentials(**access_information)

If ``scope`` contains ``identity`` then ``r.user`` will be set to the
OAuthenticated user with ``r.get_access_information`` or
``r.set_access_credentials`` unless we've set the ``update_user`` argument to
``False``.

Step 5: Use the access.
^^^^^^^^^^^^^^^^^^^^^^^

Now that we've gained access, it's time to use it.

.. code-block:: pycon

    >>> authenticated_user = r.get_me()
    >>> print authenticated_user.name, authenticated_user.link_karma

Step 6: Refreshing the access_token.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An access token lasts for 60 minutes. To get access after that period, we'll
need to refresh the access token.

.. code-block:: pycon

    >>> r.refresh_access_information(access_information['refresh_token'])

This returns a dict, where the ``access_token`` key has had it's value updated.
Neither ``scope`` or ``refresh_token`` will have changed.

.. _oauth_webserver:

An example webserver
--------------------

To run the example webserver, first install flask.

.. code-block:: bash

    $ pip install flask

Then save the code below into a file called example_webserver.py, set the
``CLIENT_ID`` & ``CLIENT_SECRET`` to the correct values and run the program.
Now you have a webserver running on http://127.0.0.1:65010 Go there and click
on one of the links. You'll be asked to authorize your own application, click
allow. Now you'll be redirected back and your user details will be written to
the screen.

.. code-block:: python

    # example_webserver.py #
    ########################

    from flask import Flask, request

    import praw

    app = Flask(__name__)

    CLIENT_ID = 'YOUR_CLIENT_ID'
    CLIENT_SECRET = 'YOUR CLIENT SECRET'
    REDIRECT_URL = 'http://127.0.0.1:65010/authorize_callback'

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
                        'github.com/praw-dev/praw/wiki/OAuth for more info.')
        r.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URL)
        app.run(debug=True, port=65010)

.. _oauth_scopes:

OAuth Scopes.
-------------

The following list of access types can be combined in any way you please. Just
give a list of the scopes you want in the scope argument of the
``get_authorize_url`` method. The description of each scope is identical to the
one users will see when they have to authorize your application.

+-----------------+-------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Type            | Description                                                                   | PRAW methods                                                                                                                                                                                             |
+=================+===============================================================================+==========================================================================================================================================================================================================+
| edit            | Edit and delete my comments and submissions.                                  | edit, delete                                                                                                                                                                                             |
+-----------------+-------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| identity        | Access my reddit username and signup date.                                    | get_me                                                                                                                                                                                                   |
+-----------------+-------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| modconfig       | Manage the configuration, sidebar, and CSS of subreddits I moderate.          | get_settings, set_settings, set_stylesheet, upload_image, create_subreddit, update_settings                                                                                                              |
+-----------------+-------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| modflair        | Manage and assign flair in subreddits I moderate.                             | add_flair_template, clear_flair_template, delete_flair, configure_flair, flair_list, set_flair, set_flair_csv                                                                                            |
+-----------------+-------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| modlog          | Access the moderation log in subreddits I moderate.                           | get_mod_log                                                                                                                                                                                              |
+-----------------+-------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| modposts        | Approve, remove, mark nsfw, and distinguish content in subreddits I moderate. | approve, distinguish, remove, mark_as_nsfw, unmark_as_nsfw, undistinguish.                                                                                                                               |
+-----------------+-------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| mysubreddits    | Access the list of subreddits I moderate, contribute to, and subscribe to.    | my_contributions, my_moderation, my_reddits                                                                                                                                                              |
+-----------------+-------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| privatemessages | Access my inbox and send private messages to other users.                     | mark_as_read, mark_as_unread, send_message, get_inbox, get_modmail, get_sent, get_unread                                                                                                                 |
+-----------------+-------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| read            | Access posts, listings and comments through my account.                       | get_comments, get_new_by_date (and the other listing funcs), get_submission, get_subreddit, get_content, from_url can now access things in private subreddits that the authenticated user has access to. |
+-----------------+-------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| submit          | Submit links and comments from my account.                                    | add_comment, reply, submit                                                                                                                                                                               |
+-----------------+-------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| subscribe       | Manage my subreddit subscriptions.                                            | subscribe, unsubscribe                                                                                                                                                                                   |
+-----------------+-------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| vote            | Submit and change my votes on comments and submissions.                       | clear_vote, upvote, downvote, vote                                                                                                                                                                       |
+-----------------+-------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
