PRAW: The Python Reddit Api Wrapper
===================================

.. image:: https://travis-ci.org/praw-dev/praw.png
        :target: https://travis-ci.org/praw-dev/praw

PRAW, an acronym for "Python Reddit API Wrapper", is a python package that
allows for simple access to reddit's API. PRAW aims to be as easy to use as
possible and is designed to follow all of `reddit's API rules
<https://github.com/reddit/reddit/wiki/API>`_. You have to give a useragent
that follows the rules, everything else is handled by PRAW so you needn't worry
about violating them.

Here's a quick peek, getting the first 5 submissions from
the 'hot' section of the 'opensource' subreddit:

.. code-block:: pycon

    >>> import praw
    >>> r = praw.Reddit(user_agent='my_cool_application')
    >>> submissions = r.get_subreddit('opensource').get_hot(limit=5)
    >>> [str(x) for x in submissions]

This will display something similar to the following:

.. code-block:: pycon

    ['10 :: Gun.io Debuts Group Funding for Open Source Projects\n Gun.io',
     '24 :: Support the Free Software Foundation',
     '67 :: The 10 Most Important Open Source Projects of 2011',
     '85 :: Plan 9 - A distributed OS with a unified communicatioprotocol  I/O...',
      '2 :: Open-source webOS is dead on arrival ']

Installation
------------

You can install via `pip <http://pypi.python.org/pypi/pip>`_

.. code-block:: bash

   $ pip install praw

Or via `easy_install <http://pypi.python.org/pypi/setuptools>`_

.. code-block:: bash

    $ easy_install praw

You can also install via ``setup.py``, this requires either a download or
checkout of the code first. Downloading PRAW from `the cheeseshop
<http://pypi.python.org/pypi/praw>`_ is recommended, as downloading from github
or doing a checkout may give you a between releases unstable codestate.

.. code-block:: bash

    # First download or checkout the code then run
    $ python setup.py install

PRAW works with Python 2.6, 2.7, 3.1, 3.2, and 3.3.

Examples and Configuration
--------------------------

For a number of simple code examples, details on PRAW's
configuration files and links to projects which use this package see the
`wiki <https://github.com/praw-dev/praw/wiki>`_.


FAQ
---

> Why is everything so slow?

Usually that has to do with how fast reddit is responding at the moment. Check
the site, see if it's responding quicker when accessing it in your browser.
Otherwise, we respect the "no more than one API call per two seconds" rule, so
if you're trying to do a bunch of quick requests in succession you're going to
be spaced out to one call per second. If you're having a specific issue besides
something covered by one of those two things, please let us know (or file a
ticket) and we'll check it out.


License
-------

All of the code contained here is licensed by the GNU GPLv3.
