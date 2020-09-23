.. _praw.ini:

praw.ini Files
==============

PRAW comes with a ``praw.ini`` file in the package directory, and looks for
user defined ``praw.ini`` files in a few other locations:

1. In the `current working directory
   <https://docs.python.org/3.6/library/os.html#os.getcwd>`_ at the time
   :class:`.Reddit` is initialized.

2. In the launching user's config directory. This directory, if available, is
   detected in order as one of the following:

   1. In the directory specified by the ``XDG_CONFIG_HOME`` environment variable on
      operating systems that define such an environment variable (some modern Linux
      distributions).

   2. In the directory specified by ``$HOME/.config`` if the ``HOME`` environment
      variable is defined (Linux and Mac OS systems).

   3. In the directory specified by the ``APPDATA`` environment variable (Windows).

   .. note::

       To check the values of the environment variables, you can open up a terminal
       (Terminal/Terminal.app/Command Prompt/Powershell) and echo the variables
       (replacing <variable> with the name of the variable):

      **MacOS/Linux**:

      .. code-block:: bash

          echo "$<variable>"

      **Windows Command Prompt**

      .. code-block:: bat

          echo "%<variable>%"

      **Powershell**

      .. code-block:: powershell

          Write-Output "$env:<variable>"

      You can also view environment variables in Python:

      .. code-block:: python

          import os
          print(os.environ.get("<variable>", ""))

Format of praw.ini
------------------

``praw.ini`` uses the `INI file format
<https://en.wikipedia.org/wiki/INI_file>`_, which can contain multiple groups of
settings separated into sections. PRAW refers to each section as a ``site``. The default
site, ``DEFAULT``, is provided in the package's ``praw.ini`` file. This site defines the
default settings for interaction with Reddit. The contents of the package's ``praw.ini``
file are:

.. literalinclude:: ../../../praw/praw.ini
   :language: ini

.. warning::

    Avoid modifying the package's ``praw.ini`` file. Prefer instead to override its
    values in your own ``praw.ini`` file. You can even override settings of the
    ``DEFAULT`` site in user defined ``praw.ini`` files.

Defining Additional Sites
-------------------------

In addition to the ``DEFAULT`` site, additional sites can be configured in user defined
``praw.ini`` files. All sites inherit settings from the ``DEFAULT`` site and can
override whichever settings desired.

Defining additional sites is a convenient way to store :ref:`OAuth credentials
<oauth_options>` for various accounts, or distinct OAuth applications. For example if
you have three separate bots, you might create a site for each:

.. _custom_site_example:
.. code-block:: ini

    [bot1]
    client_id=Y4PJOclpDQy3xZ
    client_secret=UkGLTe6oqsMk5nHCJTHLrwgvHpr
    password=pni9ubeht4wd50gk
    username=fakebot1

    [bot2]
    client_id=6abrJJdcIqbclb
    client_secret=Kcn6Bj8CClyu4FjVO77MYlTynfj
    password=mi1ky2qzpiq8s59j
    username=fakebot2

    [bot3]
    client_id=SI8pN3DSbt0zor
    client_secret=xaxkj7HNh8kwg8e5t4m6KvSrbTI
    password=1guiwevlfo00esyy
    username=fakebot3

Choosing a Site
---------------

Site selection is done via the ``site_name`` parameter to :class:`.Reddit`. For example,
to use the settings defined for ``bot2`` as shown above, initialize :class:`.Reddit`
like so:

.. code-block:: python

    reddit = praw.Reddit("bot2", user_agent="bot2 user agent")

.. note::

    In the above example you can obviate passing ``user_agent`` if you add the setting
    ``user_agent=...`` in the ``[bot2]`` site definition.

A site can also be selected via a ``praw_site`` environment variable. This approach has
precedence over the ``site_name`` parameter described above.

Using Interpolation
-------------------

By default PRAW doesn't apply any interpolation on the config file but this can be
changed with the ``config_interpolation`` parameter which can be set to "basic" or
"extended".

This can be useful to separate the components of the ``user_agent`` into individual
variables, for example:

.. _interpolation_site_example:
.. code-block:: ini

    [bot1]
    bot_name=MyBot
    bot_version=1.2.3
    bot_author=MyUser
    user_agent=script:%(bot_name)s:v%(bot_version)s (by u/%(bot_author)s)

This uses basic interpolation thus :class:`.Reddit` need to be initialized as follows:

.. code-block:: python

    reddit = praw.Reddit("bot1", config_interpolation="basic")

Then the value of ``reddit.config.user_agent`` will be ``script:MyBot:v1.2.3 (by
u/MyUser)``.

See `Interpolation of values
<https://docs.python.org/3/library/configparser.html#interpolation-of-values>`_
for details.

.. warning::

    The ConfigParser instance is cached internally at the class level, it is shared
    across all instances of :class:`.Reddit` and once set it's not overridden by future
    invocations.
