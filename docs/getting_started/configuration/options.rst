.. _configuration_options:

Configuration Options
=====================

PRAW's configuration options are broken down into the following categories:

* :ref:`basic_options`
* :ref:`oauth_options`
* :ref:`site_options`
* :ref:`misc_options`
* :ref:`custom_options`

All of these options can be provided in any of the ways mentioned in
:ref:`configuration`.

.. _basic_options:

Basic Configuration Options
---------------------------

:check_for_updates: When ``true``, check for new versions of PRAW. When a newer version
    of PRAW is available a message is reported via standard error (default: ``true``).

:user_agent: (Required) A unique description of your application. The following format
    is recommended according to `Reddit's API Rules
    <https://github.com/reddit/reddit/wiki/API#rules>`_: ``<platform>:<app ID>:<version
    string> (by u/<reddit username>)``.

.. _oauth_options:

OAuth Configuration Options
---------------------------
:client_id: (Required) The OAuth client id associated with your registered Reddit
    application. See :ref:`oauth` for instructions on registering a Reddit application.

:client_secret: The OAuth client secret associated with your registered Reddit
    application. This option is required for all application types, however, the value
    must be set to ``None`` for **installed** applications.

:redirect_uri: The redirect URI associated with your registered Reddit application. This
    field is unused for **script** applications and is only needed for both **web**
    applications, and **installed** applications when the :meth:`.url` method is used.

:password: The password of the Reddit account associated with your registered Reddit
    **script** application. This field is required for **script** applications, and PRAW
    assumes it is working with a **script** application by its presence.

:username: The username of the Reddit account associated with your registered Reddit
    **script** application. This field is required for **script** applications, and PRAW
    assumes it is working with a **script** application by its presence.

.. _site_options:

Reddit Site Configuration Options
---------------------------------

PRAW can be configured to work with instances of Reddit which are not hosted at
`reddit.com <https://www.reddit.com>`_. The following options may need to be updated in
order to successfully access a third-party Reddit site:

:comment_kind: The type prefix for comments on the Reddit instance (default: ``t1_``).

:message_kind: The type prefix for messages on the Reddit instance (default: ``t4_``).

:oauth_url: The URL used to access the Reddit instance's API (default:
            https://oauth.reddit.com).

:reddit_url: The URL used to access the Reddit instance. PRAW assumes the endpoints for
    establishing OAuth authorization are accessible under this URL (default:
    https://www.reddit.com).

:redditor_kind: The type prefix for redditors on the Reddit instance (default: ``t2_``).

:short_url: The URL used to generate short links on the Reddit instance (default:
    https://redd.it).

:submission_kind: The type prefix for submissions on the Reddit instance (default:
    ``t3_``).

:subreddit_kind: The type prefix for subreddits on the Reddit instance (default:
    ``t5_``).

.. _misc_options:

Miscellaneous Configuration Options
-----------------------------------

These are options that do not belong in another category, but still play a part in PRAW.

:check_for_async: When ``true``, check if PRAW is being ran in an asynchronous
    environment whenever a request is made. If so, a warning will be logged recommending
    the usage of `Async PRAW <https://asyncpraw.readthedocs.io/>`_. (default: ``true``)

:ratelimit_seconds: Controls the maximum amount of seconds PRAW will capture ratelimits
    returned in JSON data. Because this can be as high as 10 minutes, only ratelimits of
    up to 5 seconds are captured and waited on by default. Should be a number
    representing the amount of seconds to sleep.

    .. note::

        PRAW sleeps for the ratelimit plus either 1/10th of the ratelimit or 1 second,
        whichever is smallest.

:timeout: Controls the amount of time PRAW will wait for a request from Reddit to
    complete before throwing an exception. By default, PRAW waits 16 seconds before
    throwing an exception.

.. _custom_options:

Custom Configuration Options
----------------------------

Your application can utilize PRAW's configuration system in order to provide its own
custom settings.

For instance you might want to add an ``app_debugging: true`` option to your
application's ``praw.ini`` file. To retrieve the value of this custom option from an
instance of :class:`.Reddit` you can execute:

.. code-block:: python

   reddit.config.custom["app_debugging"]

.. note::

    Custom PRAW configuration environment variables are not supported. You can directly
    access environment variables via ``os.getenv``.
