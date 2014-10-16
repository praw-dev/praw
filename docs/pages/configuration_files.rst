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
    r = praw.Reddit(user_agent=user_agent, log_requests=1)

Config File Locations
---------------------

The configuration on all levels is stored in a file called ``praw.ini``.

The *global* configuration file is located in the **praw** package location.
This file provides the system wide default and should never be modified.

The *user* configuration file location depends on your operating system.
Assuming typical operating system installations and the username *foobar* the
path for specific operating systems should be:

* **WINDOWS XP**: C:\\Documents and Settings\\foobar\\Application
  Data\\praw.ini
* **WINDOWS Vista/7**: C:\\Users\\foobar\\AppData\\Roaming\\praw.ini
* **OS with XDG_CONFIG_HOME defined**: $XDG_CONFIG_HOME/praw.ini
* **OS X** / **Linux**: /home/foobar/.config/praw.ini

The *local* configuration file is located in the current working directory.
This location works best if you want script-specific configuration files.

Configuration Variables
-----------------------

The following variables are provided in the [DEFAULT] section of the *global*
config file. Each site can overwrite any of these variables.

* *api_request_delay*: A **float** that defines the number of seconds required
  between calls to the same domain.
* *api_domain*: A **string** that defines the *domain* to use for all
  standard API requests.
* *check_for_updates* A **boolean** to indicate whether or not to check for
  package updates.
* *cache_timeout*: An **integer** that defines the number of seconds to
  internally cache GET/POST requests based on URL.
* *decode_html_entities*: A **boolean** that controls whether or not HTML
  entities are decoded.
* *oauth_domain*: A **string** that defines the *domain* where OAuth
  authenticated requests are sent.
* *oauth_https*: A **boolean** that determines whether or not to use HTTPS for
  oauth connections. This should only be changed for development environments.
* *output_chars_limit*: A **integer** that defines the maximum length of
  unicode representations of :class:`.Comment`, :class:`.Message` and
  :class:`.Submission` objects. This is mainly used to fit them within a
  terminal window line. A negative value means no limit.
* *permalink_domain*: A **string** that defines the *domain* that is used for
   the display *permalink* for Submissions and Comments.
* *short_domain*: A **string** that defines the *domain* that is used for
   short urls.
* *timeout* Maximum time, a **float**, in seconds, before a single HTTP request
  times out. urllib2.URLError is raised upon timeout.
* *xxx_kind*: A **string** that maps the *type* returned by json results to a
  local object. **xxx** is one of: *comment*, *message*, *more*, *redditor*,
  *submission*, *subreddit*, *userlist*. This variable is needed as the
  object-to-kind mapping is created dynamically on site creation and thus isn't
  consistent across sites.
* *log_requests* A **integer** that determines the level of API call logging.

 * **0**: no logging
 * **1**: log only the request URIs
 * **2**: log the request URIs as well as any POST data

* *http_proxy* A **string** that declares a http proxy to be used. It follows
  the `requests proxy conventions
  <http://docs.python-requests.org/en/latest/user/advanced/#proxies>`_, e.g.,
  ``http_proxy: http://user:pass@addr:port``. If no proxy is specified, PRAW
  will pick up the environment variable for http_proxy, if it has been set.

* *https_proxy* A **string** that declares a https proxy to be used. It follows
  the `requests proxy conventions
  <http://docs.python-requests.org/en/latest/user/advanced/#proxies>`_, e.g.,
  ``https_proxy: http://user:pass@addr:port``. If no proxy is specified, PRAW
  will pick up the environment variable for https_proxy, if it has been set.

* *store_json_result* A **boolean** to indicate if json_dict, which contains
  the original API response, should be stored on every object in the json_dict
  attribute. Default is ``False`` as memory usage will double if enabled. For
  lazy objects, json_dict will be ``None`` until the data has been fetched.

The are additional variables that each site can define. These additional
variables are:

* *domain*: (**REQUIRED**) A **string** that provides the domain name, and
  optionally port, used to connect to the desired reddit site. For reddit
  proper, this is: `www.reddit.com`. Note that if you are running a custom
  reddit install, this name needs to match the domain name listed in the
  reddit configuration ini.
* *user*: A **string** that defines the default username to use when *login*
  is called without a *user* parameter.
* *pswd*: A **string** that defines the password to use in conjunction with
  the provided *user*.
* *ssl_domain*: A **string** that defines the *domain*  where encrypted
  requests are sent. This is used for logging in, both OAuth and user/password.
  When not provided, these requests are sent in plaintext (unencrypted).
* *oauth_client_id:* A **string** that, if given, defines the ``client_id`` a
  reddit object is initialized with.
* *oauth_client_secret:* A **string** that, if given, defines the
  ``client_secret`` a reddit object is initialized with.
* *oauth_redirect_uri* A **string** that, if given, defines the
  ``redirect_uri`` a reddit object is initialized with. If *oauth_client_id*
  and *oauth_client_secret* is also given, then :meth:`.get_authorize_url` can
  be run without first setting the oauth settings with running
  :meth:`.set_oauth_app_info`.

Note: The tracking for *api_request_delay* and *cache_timeout* is on a
per-domain, not per-site, basis. Essentially, this means that the time since
the last request is the time since the last request from any site to the domain
in question. Thus, unexpected event timings may occur if these values differ
between sites to the same domain.

The Sites
^^^^^^^^^

The default provided sites are:

* *reddit*: This site defines the settings for reddit proper. It is used by
  default if the *site* parameter is not defined when creating the *Reddit*
  object.
* *local*: This site defines settings for a locally running instance of reddit.
  The *xxx_kind* mappings may differ so you may need to shadow (overwrite) the
  'local' site in your *user*-level or *local*-level ``praw.ini`` file.

Additional sites can be added to represent other instances of reddit or simply
provide an additional set of credentials for easy access to that account.

Example praw.ini file
^^^^^^^^^^^^^^^^^^^^^

The following is an example ``praw.ini`` file which has 4 sites defined: 2 for
a reddit proper accounts and 2 for local reddit testing.

.. code-block:: text

    [bboe]
    domain: www.reddit.com
    ssl_domain: ssl.reddit.com
    user: bboe
    pswd: this_isn't_my_password

    [reddit_dev]
    domain: www.reddit.com
    ssl_domain: ssl.reddit.com
    user: someuser
    pswd: somepass

    [local_dev1]
    domain: reddit.local:8000
    user: someuser
    pswd: somepass

    [local_wacky_dev]
    domain: reddit.local:8000
    user: someuser
    pswd: somepass
    api_request_delay: 5.0
    default_content_limit: 2
