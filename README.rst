.. _main_page:

PRAW: The Python Reddit Api Wrapper
===================================

.. begin_description

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

.. end_description

.. begin_installation

Installation
------------

PRAW works with python 2.6, 2.7, 3.1, 3.2, and 3.3. The recommended way to
install is via `pip <http://pypi.python.org/pypi/pip>`_

.. code-block:: bash

   $ pip install praw

Alternatively you can do it via
`easy_install <http://pypi.python.org/pypi/setuptools>`_

.. code-block:: bash

    $ easy_install praw

.. end_installation

.. begin_support

Support
-------

The official place to ask questions about PRAW, reddit and other API wrappers
is `r/redditdev <http://www.reddit.com/r/redditdev>`_. If the question is more
about Python and less about PRAW, such as "what are generators", then you're
likely to get more, faster and more in-depth answers in `r/learnpython
<http://www.reddit.com/r/learnpython>`_.

If you've uncovered a bug or have a feature request, then `make an issue on our
project page at github <https://github.com/praw-dev/praw/issues>`_.

.. end_support

Documentation
-------------

PRAW's documentation, which includes tutorials, information on configuring PRAW
and other good stuff can be found at `readthedocs
<https://praw.readthedocs.org>`_.

.. begin_license

License
-------

All of the code contained here is licensed by
`the GNU GPLv3 <https://github.com/praw-dev/praw/blob/master/COPYING>`_.

.. end_license
