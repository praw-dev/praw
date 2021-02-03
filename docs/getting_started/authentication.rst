.. _oauth:

Authenticating via OAuth
========================

PRAW supports the three types of applications that can be registered on
Reddit. Those are:

* `Web Applications <https://github.com/reddit-archive/reddit/wiki/OAuth2-App-Types#web-app>`_
* `Installed Applications <https://github.com/reddit-archive/reddit/wiki/OAuth2-App-Types#installed-app>`_
* `Script Applications <https://github.com/reddit-archive/reddit/wiki/OAuth2-App-Types#script-app>`_

Before you can use any one of these with PRAW, you must first `register
<https://www.reddit.com/prefs/apps/>`_ an application of the appropriate type
on Reddit.

If your app does not require a user context, it is :ref:`read-only <read_only_application>`.

PRAW supports the flows that each of these applications can use. The
following table defines which tables can use which flows:

.. rst-class:: center_table_items

+-------------------+-----------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------+---------------------------------+
|  Application Type |                                          Script                                         |                                           Web                                           |            Installed            |
+===================+=========================================================================================+=========================================================================================+=================================+
|    Default Flow   |                             :ref:`Password <password_flow>`                             |                                                  :ref:`Code <code_flow>`                                                  |
+-------------------+-----------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------+---------------------------------+
|                   |                                 :ref:`Code <code_flow>`                                 |                                                                                         |                                 |
+                   +-----------------------------------------------------------------------------------------+                     :ref:`application_only_client_credentials_flow`                     + :ref:`Implicit <implicit_flow>` +
| Alternative Flows |                     :ref:`application_only_client_credentials_flow`                     |                                                                                         |                                 |
+                   +-----------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------+---------------------------------+
|                   |                                                                                    :ref:`application_only_installed_client_flow`                                                                                    |
+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. _password_flow:

Password Flow
-------------

**Password Flow** is the simplest type of authentication flow to work with
because no callback process is involved in obtaining an ``access_token``.

While **password flow** applications do not involve a redirect URI, Reddit
still requires that you provide one when registering your script application --
``http://localhost:8080`` is a simple one to use.

In order to use a **password flow** application with PRAW you need four pieces
of information:

:client_id: The client ID is the 14-character string listed just under
            "personal use script" for the desired `developed application
            <https://www.reddit.com/prefs/apps/>`_

:client_secret: The client secret is at least a 27-character string listed adjacent to
                ``secret`` for the application.

:password: The password for the Reddit account used to register the application.

:username: The username of the Reddit account used to register the application.

With this information authorizing as ``username`` using a **password flow** app
is as simple as:

.. code-block:: python

   reddit = praw.Reddit(client_id="SI8pN3DSbt0zor",
                        client_secret="xaxkj7HNh8kwg8e5t4m6KvSrbTI",
                        password="1guiwevlfo00esyy",
                        user_agent="testscript by u/fakebot3",
                        username="fakebot3")

To verify that you are authenticated as the correct user run:

.. code-block:: python

   print(reddit.user.me())

The output should contain the same name as you entered for ``username``.

.. note::

    If the following exception is raised, double-check your credentials, and ensure that
    that the username and password you are using are for the same user with which the
    application is associated:

    .. code-block::

        OAuthException: invalid_grant error processing request

.. _2FA:

Two-Factor Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~

A 2FA token can be used by joining it to the password with a colon:

.. code-block:: python

   reddit = praw.Reddit(client_id="SI8pN3DSbt0zor",
                        client_secret="xaxkj7HNh8kwg8e5t4m6KvSrbTI",
                        password='1guiwevlfo00esyy:955413',
                        user_agent="testscript by u/fakebot3",
                        username="fakebot3")

However, for such an app there is little benefit to using 2FA. The token
must be refreshed after one hour; therefore, the 2FA secret would have to be
stored along with the rest of the credentials in order to generate the token,
which defeats the point of having an extra credential beyond the password.

If you do choose to use 2FA, you must handle the ``prawcore.OAuthException``
that will be raised by API calls after one hour.


.. _code_flow:

Code Flow
---------

A **code flow** application is useful for two primary purposes:

* You have an application and want to be able to access Reddit from your users'
  accounts.
* You have a personal-use script application and you either want to

   * limit the access one of your PRAW-based programs has to Reddit
   * avoid the hassle of 2FA (described above)
   * not pass your username and password to PRAW (and thus not keep it in memory)

When registering your application you must provide a valid redirect URI. If you are
running a website you will want to enter the appropriate callback URL and configure that
endpoint to complete the code flow.

If you aren't actually running a website, you can use the :ref:`refresh_token` script to
obtain ``refresh_tokens``. Enter ``http://localhost:8080`` as the redirect URI when
using this script.

Whether or not you use the script there are two processes involved in obtaining
access or refresh tokens.

.. _auth_url:

Obtain the Authorization URL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first step to completing the **code flow** is to obtain the authorization
URL. You can do that as follows:

.. code-block:: python

    reddit = praw.Reddit(client_id="SI8pN3DSbt0zor",
         client_secret="xaxkj7HNh8kwg8e5t4m6KvSrbTI",
         redirect_uri="http://localhost:8080",
         user_agent="testscript by u/fakebot3"
    )
    print(reddit.auth.url(["identity"], "...", "permanent"))

The above will output an authorization URL for a permanent token that has only the
`identity` scope. See :meth:`.url` for more information on these parameters.

This URL should be accessed by the account that desires to authorize their Reddit access
to your application. On completion of that flow, the user's browser will be redirected
to the specified ``redirect_uri``. After extracting verifying the ``state`` and
extracting the ``code`` you can obtain the refresh token via:

.. code-block:: python

     print(reddit.auth.authorize(code))
     print(reddit.user.me())

The first line of output is the ``refresh_token``. You can save this for later use (see
:ref:`using_refresh_token`).

The second line of output reveals the name of the Redditor that completed the code flow.
It also indicates that the ``reddit`` instance is now associated with that account.

The code flow can be used with an **installed** application just as described above with
one change: set the value of ``client_secret`` to ``None`` when initializing
:class:`.Reddit`.

.. _implicit_flow:

Implicit Flow
-------------

The **implicit flow** requires a similar instantiation of the :class:`.Reddit` class as
done in :ref:`code_flow`, however, the token is returned directly as part of the
redirect. For the implicit flow call :meth:`.url` like so:

.. code-block:: python

    print(reddit.auth.url(["identity"], "...", implicit=True))

Then use :meth:`.implicit` to provide the authorization to the :class:`.Reddit`
instance.

.. _read_only_application:

Read-Only Mode
--------------

All application types support a read-only mode. Read-only mode provides access to Reddit
like a logged out user would see including the default Subreddits in the
``reddit.front`` listings.

In the absence of a ``refresh_token`` both :ref:`code_flow` and :ref:`implicit_flow`
applications start in the **read-only** mode. With such applications **read-only** mode
is disabled when :meth:`.authorize`, or :meth:`.implicit` are successfully called.
:ref:`password_flow` applications start up with **read-only** mode disabled.

Read-only mode can be toggled via:

.. code-block:: python

   # Enable read-only mode
   reddit.read_only = True

   # Disable read-only mode (must have a valid authorization)
   reddit.read_only = False


Application-Only Flows
~~~~~~~~~~~~~~~~~~~~~~

The following flows are the **read-only mode** flows for Reddit applications

.. _application_only_client_credentials_flow:

Application-Only (Client Credentials)
+++++++++++++++++++++++++++++++++++++

This is the default flow for **read-only mode** in script and web applications. The idea
behind this is that Reddit *can* trust these applications as coming from a given
developer, however the application requires no logged-in user context.

An installed application *cannot* use this flow, because Reddit requires a
``client_secret`` to be given it this flow is being used. In other words, installed
applications are not considered confidential clients.

.. _application_only_installed_client_flow:

Application-Only (Installed Client)
+++++++++++++++++++++++++++++++++++

This is the default flow for **read-only mode** in installed applications. The idea
behind this is that Reddit *might not be able* to trust these applications as coming
from a given developer. This would be able to happen if someone other than the developer
can potentially replicate the client information and then pretend to be the application,
such as in installed applications where the end user could retrieve the ``client_id``.

.. note::

    No benefit is really gained from this in script or web apps. The one exception is
    for when a script or web app has multiple end users, this will allow you to give
    Reddit the information needed in order to distinguish different users of your app
    from each other (as the supplied device id *should* be a unique string per both
    device (in the case of a web app, server) and user (in the case of a web app,
    browser session).

.. _using_refresh_token:

Using a Saved Refresh Token
---------------------------

A saved refresh token can be used to immediately obtain an authorized instance of
:class:`.Reddit` like so:

.. code-block:: python

    reddit = praw.Reddit(client_id="SI8pN3DSbt0zor",
        client_secret="xaxkj7HNh8kwg8e5t4m6KvSrbTI",
        refresh_token="WeheY7PwgeCZj4S3QgUcLhKE5S2s4eAYdxM",
        user_agent="testscript by u/fakebot3"
    )
    print(reddit.auth.scopes())

The output from the above code displays which scopes are available on the
:class:`.Reddit` instance.

.. note::

    Observe that ``redirect_uri`` does not need to be provided in such cases. It is only
    needed when :meth:`.url` is used.
