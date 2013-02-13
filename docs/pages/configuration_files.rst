.. _configuration_files:

The Configuration Files
=======================

The `PRAW <https://github.com/praw-dev/praw>`_ comes with a file,
``praw/praw.ini`` which provides the default global variables for reddit sites,
as well as defines two sites.

Config File Locations
---------------------

There are three locations that PRAW searches and loads ``praw.ini`` files:

The first location, _global_, is in the **praw** package location. This file
provides the system wide defaults. This file should never be modified.

The second location, _user_, depends on your operating system. Assuming typical
operating system installations and the username _foobar_ the path for specific
operating systems should be:

* **WINDOWS XP**: C:\\Documents and Settings\\foobar\\Application
  Data\\praw.ini
* **WINDOWS Vista/7**: C:\\Users\\foobar\\AppData\\Roaming\\praw.ini
* **OS with XDG_CONFIG_HOME defined**: $XDG_CONFIG_HOME/praw.ini
* **OS X** / **Linux**: /home/foobar/.config/praw.ini

The final location, _local_, is the current working directory. This location
works best if you want script-specific configuration files.

Note, that while the settings contained in these file are addative, in cases
where the same site and variables are defined in multiple files the _local_
settings take precedence, followed by the _user_ settings, and finally the
_global_ settings.

Config File Variables
---------------------

The following variables are provided in the [DEFAULT] section of the _global_
config file. Each site can overwrite any of these variables.

* _api_request_delay_: A **float** that defines the number of seconds required
  between calls to the same domain.
* _cache_timeout_: An **integer** that defines the number of seconds to
  internally cache GET/POST requests based on URL.
* _default_content_limit_: An **integer** that defines the default maximum
  number of results to fetch in a single request for API requests that are
  potentially unbounded such as _get_front_page_, _get_inbox_, and
  _flairlist_.
* _xxx_kind_: A **string** that maps the _type_ returned by json results to a
  local object. **xxx** is one of: _comment_, _message_, _more_, _redditor_,
  _submission_, _subreddit_, _userlist_. This mapping is needed as the
  mappings are created dynamically on site creation and thus isn't consistent
  across sites.

The are additional variables that each site can define. These additional
variables are:

* _domain_: (**REQUIRED**) A **string** that provides the domain name, and
  optionally port, used to connect to the desired reddit site. For reddit
  proper, this is: `www.reddit.com`. Note that if you are running a custom
  reddit install, this name needs to match the domain name listed in the
  reddit configuration ini.
* _ssl_domain_: If provided, it is a **string** similar to _domain_ which is
  used to make encrypted requests. Currently this is only used for the _login_
  method. When not provided, these requests are sent in plaintext
  (unencrypted).
* _user_: A **string** that defines the default username to use when _login_
  is called without a _user_ parameter.
* _pswd_: A **string** that defines the password to use in conjunction with
  the provided _user_.

Please note that while the _api_request_delay_ and _cache_timeout_ can be
defined for different sites which point to the same domain, the tracking for
each occurs on a per-domain, and not per-site, basis. Essentially, this
per-domain tracking means that the time since the last request is the time
since the last request from any site to the domain in question. Thus,
unexpected event timings may occur if these values differ between sites to the
same domain.

The Sites
^^^^^^^^^

The default provided sites are:

* _reddit_: This site defines the settings for reddit proper. It is also used
  by default if the _site_ parameter is not defined when creating the
  _Reddit_ object.
* _local_: This site defines settings for a locally running instance of
  reddit. The _xxx_kind_ mappings may differ so you may need to shadow
  (overwrite) the 'local' site in your _user_-level or _local_-level
  ``praw.ini`` file.

Additional sites can be added to both represent other installations of reddit
on other servers, or to simply provide an additional set of credentials for
easy access to that account.

Example praw.ini file
^^^^^^^^^^^^^^^^^^^^^

The following is an example ``praw.ini`` file which has 4 sites defined. 2 for
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
