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

   1. In the directory specified by the ``XDG_CONFIG_HOME`` environment
      varaible on operating systems that define such an environment variable
      (some modern Linux distributions).

   2. In the directory specified by ``$HOME/.config`` if the ``HOME``
      environment variable is defined (Linux and Mac OS systems).

   3. In the directory specified by the ``APPDATA`` environment variable
      (Windows).


Format of praw.ini
------------------

``praw.ini`` uses the `INI file format
<https://en.wikipedia.org/wiki/INI_file>`_, which can contain multiple groups
of settings separated into sections. PRAW refers to each section as a
``site``. The default site, ``DEFAULT``, is provided in the package's
``praw.ini`` file. This site defines the default settings for interaction with
Reddit. The contents of the package's ``praw.ini`` file are:

.. literalinclude:: ../../../praw/praw.ini
   :language: ini

.. warning:: Avoid modifying the package's ``praw.ini`` file. Prefer instead to
             override its values in your own ``praw.ini`` file. You can even
             override settings of the ``DEFAULT`` site in user defined
             ``praw.ini`` files.

Defining Additional Sites
-------------------------

In addition to the ``DEFAULT`` site, additional sites can be configured in user
defined ``praw.ini`` files. All sites inherit settings from the ``DEFAULT``
site and can override whichever settings desired.

Defining additional sites is a convenient way to store :ref:`OAuth credentials
<oauth_options>` for various accounts, or distinct OAuth applications. For
example if you have three separate bots, you might create a site for each:

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

Site selection is done via the ``site_name`` parameter to :class:`.Reddit`. For
example, to use the settings defined for ``bot2`` as shown above, initialize
:class:`.Reddit` like so:

.. code-block:: python

   reddit = praw.Reddit('bot2', user_agent='bot2 user agent')

.. note:: In the above example you can obviate passing ``user_agent`` if you
          add the setting ``user_agent=...`` in the ``[bot2]`` site definition.

A site can also be selected via a ``praw_site`` environment variable. This
approach has precedence over the ``site_name`` parameter described above.
