.. _oauth:

Authenticating via OAuth
========================

PRAW supports the three types of applications that can be registered on
Reddit. Those are:

* :ref:`script_application`
* :ref:`web_application`
* :ref:`installed_application`

Before you can use any one of these with PRAW, you must first `register
<https://www.reddit.com/prefs/apps/>`_ an application of the appropriate type
on Reddit.

.. _script_application:

Script Application
------------------

**Script** applications are the simplest type of application to work with
because they don't involve any sort of callback process to obtain an
``access_token``.

While **script** applications do not involve a redirect uri, Reddit still
requires that you provide one when registering your application --
``http://localhost:8080`` is a simple one to use.

In order to use a **script** application with PRAW you need four pieces of
information:

:client_id: The client ID is the 14 character string listed just under
            "personal use script" for the desired `developed application
            <https://www.reddit.com/prefs/apps/>`_

:client_secret: The client secret is the 27 character string listed adjacent to
                ``secret`` for the application.

:password: The password for the Reddit account used to register the **script**
           application.

:username: The username of the Reddit account used to register the **script**
           application.

With this information authorizing as ``username`` using a **script** app is as
simple as:

.. code-block:: python

   reddit = praw.Reddit(client_id='SI8pN3DSbt0zor',
                        client_secret='xaxkj7HNh8kwg8e5t4m6KvSrbTI',
                        password='1guiwevlfo00esyy',
                        user_agent='testscript by /u/fakebot3',
                        username='fakebot3')

To verify that you are authenticated as the correct user run:

.. code-block:: python

   print(reddit.user.me())

The output should contain the same name as you entered for ``username``.

.. note:: If the following exception is raised, double check your credentials,
          and ensure that that the username and password you are using are for
          the same user with which the script application is associated:

          .. code::

             OAuthException: invalid_grant error processing request


.. _web_application:

Web Application
---------------

A **web** application is useful for two primary purposes:

* You have a website and want to be able to access Reddit from your users'
  accounts.
* You want to limit the access one of your PRAW-based programs has to Reddit,
  or simply do not want to pass your username and password to PRAW.

When registering a **web** application you must provide a valid redirect
uri. If you are running a website you will want to enter the appropriate
callback URL and configure that endpoint to complete the code flow.

If you aren't actually running a website, you can use the :ref:`refresh_token`
script to obtain ``refresh_tokens``. Enter ``http://localhost:8080`` as the
redirect uri when using this script.

Whether or not you use the script there are two processes involved in obtaining
access or refresh tokens.

.. _auth_url:

Obtain the Authorization URL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first step to completing the **web** application code flow is to obtain
the authorization URL. You can do that as follows:

.. code-block:: python

   reddit = praw.Reddit(client_id='SI8pN3DSbt0zor',
                        client_secret='xaxkj7HNh8kwg8e5t4m6KvSrbTI',
                        redirect_uri='http://localhost:8080',
                        user_agent='testscript by /u/fakebot3')
   print(reddit.auth.url(['identity'], '...', 'permanent'))

The above will output an authorization URL for a permanent token that has only
the `identity` scope. See :meth:`.url` for more information on these
parameters.

This URL should be accessed by the account that desires to authorize their
Reddit access to your application. On completion of that flow, the user's
browser will be redirected to the specified ``redirect_uri``. After extracting
verifying the ``state`` and extracting the ``code`` you can obtain the refresh
token via:

.. code-block:: python

    print(reddit.auth.authorize(code))
    print(reddit.user.me())

The first line of output is the ``refresh_token``. You can save this for later
use (see :ref:`using_refresh_token`).

The second line of output reveals the name of the Redditor that completed the
**web** application code flow. It also indicates that the ``reddit`` instance
is now associated with that account.

.. _installed_application:

Installed Application
---------------------

The code flow can be used with an **installed** application just as described
above with one change: set the value of ``client_secret`` to ``None`` when
initializing :class:`.Reddit`.

The implicit flow is similar, however, the token is returned directly as part
of the redirect. For the implicit flow call :meth:`.url` like so:

.. code-block:: python

   print(reddit.auth.url(['identity'], '...', implicit=True)

Then use :meth:`.implicit` to provide the authorization to the :class:`.Reddit`
instance.

.. _using_refresh_token:

Using a Saved Refresh Token
---------------------------

A saved refresh token can be used to immediately obtain an authorized instance
of :class:`.Reddit` like so:

.. code-block:: python

   reddit = praw.Reddit(client_id='SI8pN3DSbt0zor',
                        client_secret='xaxkj7HNh8kwg8e5t4m6KvSrbTI',
                        refresh_token='WeheY7PwgeCZj4S3QgUcLhKE5S2s4eAYdxM',
                        user_agent='testscript by /u/fakebot3')
   print(reddit.auth.scopes())

The output from the above code displays which scopes are available on the
:class:`.Reddit` instance.

.. note:: Observe that ``redirect_uri`` does not need to be provided in such
          cases. It is only needed when :meth:`.url` is used.

Read Only Mode
--------------

All application types support a read only mode. Read only mode provides access
to Reddit like a logged out user would see including the default Subreddits in
the ``reddit.front`` listings.

In the absence of a ``refresh_token`` both **web** and **installed**
applications start in the **read only** mode. With such applications **read
only** mode is disabled when :meth:`.authorize`, :meth:`.implicit` are
successfully called. **Script** applications start up with **read only** mode
disabled.

Read only mode can be toggled via:

.. code-block:: python

   # Enable read only mode
   reddit.read_only = True

   # Disable read only mode (must have a valid authorization)
   reddit.read_only = False
