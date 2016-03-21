.. _configuration_files:

The Configuration Files
=======================

PRAW can be configured on the global, user, local and ``Reddit`` instance
levels. This allows for easy custom configuration to fit your needs.

To build the configuration settings, first the global configuration file is
loaded. It contains the default settings for all PRAW applications and should
never be modified. Then PRAW opens the user level configuration file (if it
exists) and any settings here will take precedence over those in the global
configuration file. Then PRAW opens the local level configuration file (if it
exists) and any settings here will take precedence over those previously
defined. Finally you can set configuration settings by giving them as
additional arguments when instantiating the ``Reddit`` object. Settings given
this way will take precedence over those previously defined.

.. code-block:: python

    import praw

    user_agent = ("Configuration setting example by /u/_Daimon_. See "
                  "https://praw.readthedocs.org/en/latest/pages/configuration_files.html")
    r = praw.Reddit(user_agent=user_agent)

Config File Locations
---------------------

The configuration on all levels is stored in a file called ``praw.ini``.

The *global* configuration file is located in the **praw** package location.
This file provides the system wide default and should never be modified.

The *user* configuration file location depends on your operating system.
Assuming typical operating system installations and the username *foobar* the
path for specific operating systems should be:

* **WINDOWS XP:** C:\\Documents and Settings\\foobar\\Application
  Data\\praw.ini
* **WINDOWS Vista/7:** C:\\Users\\foobar\\AppData\\Roaming\\praw.ini
* **OS with XDG_CONFIG_HOME defined:** $XDG_CONFIG_HOME/praw.ini
* **OS X** / **Linux:** /home/foobar/.config/praw.ini

The *local* configuration file is located in the current working directory.
This location works best if you want script-specific configuration files.

Configuration Variables
-----------------------

The following variables are provided in the [DEFAULT] section of the *global*
config file. Each site can overwrite any of these variables.

* *check_for_updates:* A **boolean** to indicate whether or not to check for
  package updates.
* *http_proxy:* A **string** that declares a http proxy to be used. It follows
  the `requests proxy conventions
  <http://docs.python-requests.org/en/latest/user/advanced/#proxies>`_, e.g.,
  ``http_proxy: http://user:pass@addr:port``. If no proxy is specified, PRAW
  will pick up the environment variable for http_proxy, if it has been set.
* *https_proxy:* A **string** that declares a https proxy to be used. It
  follows the `requests proxy conventions
  <http://docs.python-requests.org/en/latest/user/advanced/#proxies>`_, e.g.,
  ``https_proxy: http://user:pass@addr:port``. If no proxy is specified, PRAW
  will pick up the environment variable for https_proxy, if it has been set.
* *oauth_url:* A **string** that defines the *scheme* and *domain* where OAuth
  authenticated requests are sent.
* *reddit_url:* A **string** that defines the *scheme* and *domain* that is
   used to regularly access the site.
* *short_url:* A **string** that defines the *scheme* and *domain* that is used
   for short urls to the site.
* *store_json_result:* A **boolean** to indicate if json_dict, which contains
  the original API response, should be stored on every object in the json_dict
  attribute. Default is ``False`` as memory usage will double if enabled. For
  lazy objects, json_dict will be ``None`` until the data has been fetched.
* *xxx_kind:* A **string** that maps the *type* returned by json results to a
  local object. **xxx** is one of: *comment*, *message*, *more*, *redditor*,
  *submission*, *subreddit*, *userlist*. This variable is needed as the
  object-to-kind mapping is created dynamically on site creation and thus isn't
  consistent across sites.



The are additional variables that each site can define. These additional
variables are:

* *client_id:* A **string** that, if given, defines the ``client_id`` a
  reddit object is initialized with.
* *client_secret:* A **string** that, if given, defines the
  ``client_secret`` a reddit object is initialized with.
* *redirect_uri:* A **string** that, if given, defines the ``redirect_uri`` a
  reddit object is initialized with. If *client_id* and *client_secret* is also
  given, then :meth:`.get_authorize_url` can be run without first setting the
  oauth settings with running :meth:`.set_oauth_app_info`.
* *refresh_token:* A **string** that, if given, defines the ``refresh_token`` a
  reddit object is initialized with. If *client_id*,
  *client_secret*, and *redirect_uri* are also given, then
  :meth:`~praw.__init__.AuthenticatedReddit.refresh_access_information` can be
  run with no arguments to acquire new access information without first running
  :meth:`.get_authorize_url` and
  :meth:`~praw.__init__.AuthenticatedReddit.get_access_information`.

The Sites
^^^^^^^^^

The default provided sites are:

* *reddit:* This site defines the settings for reddit proper. It is used by
  default if the *site* parameter is not defined when creating the *Reddit*
  object.
* *local:* This site defines settings for a locally running instance of reddit.
  The *xxx_kind* mappings may differ so you may need to shadow (overwrite) the
  'local' site in your *user*-level or *local*-level ``praw.ini`` file.

Additional sites can be added to represent other instances of reddit or simply
provide an additional set of credentials for easy access to that account. This
is done by adding ``[YOUR_SITE]`` to the ``praw.ini`` file and then calling it
in :class:`praw.Reddit`. For example, you could add the following to your
``praw.ini`` file:

.. code-block:: text

    [YOUR_SITE]
    oauth_url: http://reddit.local
    reddit_url: http://reddit.local

From there, to specify the reddit instance of "YOUR_SITE", you would do
something like this:

.. code-block:: python

    import praw

    r = praw.Reddit(user_agent='Custom Site Example for PRAW',
                    site_name='YOUR_SITE')

Of course, you can use any of the above Configuration Variables as well.
