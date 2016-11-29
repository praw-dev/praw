PRAW: The Python Reddit API Wrapper
===================================

.. image:: https://img.shields.io/pypi/v/praw.svg
   :alt: Latest PRAW Version
   :target: https://pypi.python.org/pypi/praw
.. image:: https://travis-ci.org/praw-dev/praw.svg?branch=master
   :alt: Travis CI Status
   :target: https://travis-ci.org/praw-dev/praw
.. image:: https://coveralls.io/repos/github/praw-dev/praw/badge.svg?branch=master
   :alt: Coveralls Coverage
   :target: https://coveralls.io/github/praw-dev/praw?branch=master
.. image:: https://badges.gitter.im/praw-dev/praw.svg
   :alt: Join the chat at https://gitter.im/praw-dev/praw
   :target: https://gitter.im/praw-dev/praw
.. image:: https://img.shields.io/badge/donate-cash.me%2F%24praw-blue.svg
   :alt: Donate via https://cash.me/$praw
   :target: https://cash.me/$praw

PRAW, an acronym for "Python Reddit API Wrapper", is a python package that
allows for simple access to Reddit's API. PRAW aims to be easy to use and
internally follows all of `Reddit's API rules
<https://github.com/reddit/reddit/wiki/API>`_. With PRAW there's no need to
introduce ``sleep`` calls in your code. Give your client an appropriate user
agent and you're set.

.. _installation:

Installation
------------

PRAW is supported on python 2.7, 3.3, 3.4, and 3.5. The recommended way to
install PRAW is via `pip <https://pypi.python.org/pypi/pip>`_.

.. code-block:: bash

   pip install praw

To install the latest development version of PRAW run the following instead:

.. code-block:: bash

   pip install --upgrade https://github.com/praw-dev/praw/archive/master.zip

For instructions on installing python and pip see "The Hitchhiker's Guide to
Python" `Installation Guides
<http://docs.python-guide.org/en/latest/starting/installation/>`_.

Quickstart
----------

Assuming you already have a credentials for a script-type OAuth application you
can instantiate an instance of PRAW like so:

.. code-block:: python

  import praw
  reddit = praw.Reddit(client_id='CLIENT_ID', client_secret="CLIENT_SECRET",
                       password='PASSWORD', user_agent='USERAGENT',
                       username='USERNAME')

With the ``reddit`` instance you can then interact with Reddit:

.. code-block:: python

  # Create a submission to /r/test
  reddit.subreddit('test').submit('Test Submission', url='https://reddit.com')

  # Comment on a known submission
  submission = reddit.submission(url='https://www.reddit.com/comments/5e1az9')
  submission.reply('Super rad!')

  # Reply to the first comment of a weekly top thread of a moderated community
  submission = next(reddit.subreddit('mod').top('week'))
  submission.comments[0].reply('An automated reply')

  # Output score for the first 256 items on the frontpage
  for submission in reddit.front.hot(limit=256):
      print(submission.score)

  # Obtain the moderator listing for redditdev
  for moderator in reddit.subreddit('redditdev').moderator:
      print(moderator)

Please see PRAW's `documentation <http://praw.readthedocs.io/>`_ for
more examples of what you can do with PRAW.

PRAW Discussion and Support
---------------------------

For those new to python, or would otherwise consider themselves a python
beginner, please consider asking questions on the `r/learnpython
<https://www.reddit.com/r/learnpython>`_ subreddit. There are wonderful people
there who can help with general python and simple PRAW related questions.

Otherwise, there are a few official places to ask questions about PRAW:

`/r/redditdev <https://www.reddit.com/r/redditdev>`_ is the best place on
Reddit to ask PRAW related questions. This subreddit is for all Reddit API
related discussion so please tag submissions with *[PRAW]*. Please perform a
search on the subreddit first to see if anyone has similar questions.

Real-time chat can be conducted via the `praw-dev/praw
<https://gitter.im/praw-dev/praw>`_ channel on gitter.

Please do not directly message any of the contributors via Reddit, email, or
gitter unless they have indicated otherwise. We strongly encourage everyone to
help others with their questions.

Please file bugs and feature requests as issues on `GitHub
<https://github.com/praw-dev/praw/issues>`_ after first searching to ensure a
similar issue was not already filed. If such an issue already exists please
give it a thumbs up reaction. Comments to issues containing additional
information are certainly welcome.

.. note:: This project is released with a `Contributor Code of Conduct
   <https://github.com/praw-dev/praw/blob/master/CODE_OF_CONDUCT.md>`_. By
   participating in this project you agree to abide by its terms.

Documentation
-------------

PRAW's documentation is located at http://praw.readthedocs.io/.

History
-------

`August 2010
<https://github.com/praw-dev/praw/commit/efef08a4a713fcfd7dfddf992097cf89426586ae>`_:
Timothy Mellor created a github project called ``reddit_api``.

`March 2011
<https://github.com/praw-dev/praw/commit/ebfc9caba5b58b9e68c77af9c8e53f5562a2ee64>`_:
The python package ``reddit`` was registered and uploaded to pypi.

`December 2011
<https://github.com/praw-dev/praw/commit/74bb962b3eefe04ce6acad88e6f53f43d10c8803>`_:
Bryce Boe took over as maintainer of the ``reddit`` package.

`June 2012
<https://github.com/praw-dev/praw/commit/adaf89fe8631f41ab9913b379de104c9ef6a1e73>`_:
Bryce renamed the project ``PRAW`` and the repository was relocated to the
newly created praw-dev organization on GitHub.

`February 2016
<https://github.com/praw-dev/praw/commit/252083ef1dbfe6ea53c2dc99ac235b4ba330b658>`_:
Bryce began work on PRAW4, a complete rewrite of PRAW.


License
-------

PRAW's source (v4.0.0+) is provided under the `Simplified BSD License
<https://github.com/praw-dev/praw/blob/0860c11a9309c80621c267af7caeb6a993933744/LICENSE.txt>`_.

* Copyright (c), 2016, Bryce Boe

Earlier versions of PRAW were released under `GPLv3
<https://github.com/praw-dev/praw/blob/0c88697fdc26e75f87b68e2feb11e101e90ce215/COPYING>`_.

Donations
---------

Please consider donating to PRAW's maintainer via https://cash.me/$praw.
