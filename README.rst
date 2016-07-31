PRAW: The Python Reddit API Wrapper
===================================

.. image:: https://travis-ci.org/praw-dev/praw.svg?branch=praw4
   :alt: Travis CI Status
   :target: https://travis-ci.org/praw-dev/praw
.. image:: https://coveralls.io/repos/github/praw-dev/praw/badge.svg?branch=praw4
   :alt: Coveralls Coverage
   :target: https://coveralls.io/github/praw-dev/praw?branch=praw4
.. image:: https://badges.gitter.im/praw-dev/praw.svg
   :alt: Join the chat at https://gitter.im/praw-dev/praw
   :target: https://gitter.im/praw-dev/praw
.. image:: https://img.shields.io/badge/donate-cash.me%2F%24praw-blue.svg
   :alt: Donate via https://cash.me/$praw
   :target: https://cash.me/$praw

PRAW, an acronym for "Python Reddit API Wrapper", is a python package that
allows for simple access to reddit's API. PRAW aims to be easy to use and
internally follows all of `reddit's API rules
<https://github.com/reddit/reddit/wiki/API>`_. With PRAW there's no need to
introduce ``sleep`` calls in your code. Give your client an appropriate user
agent and you're set.

.. _installation:

Installation
------------

PRAW is supported on python 2.7, 3.3, 3.4, and 3.5. The recommended way to
install PRAW is via `pip <https://pypi.python.org/pypi/pip>`_.

.. code-block:: bash

    pip install --pre praw

.. note:: The ``--pre`` flag is needed to install PRAW4 as it is not yet the
   official version.

To install the latest development version of PRAW4 run the following instead:

.. code-block:: bash

    pip install --upgrade https://github.com/praw-dev/praw/archive/praw4.zip

For instructions on installing python and pip see "The Hitchhiker's Guide to
Python" `Installation Guides
<http://docs.python-guide.org/en/latest/starting/installation/>`_.

PRAW Discussion and Support
---------------------------

For those new to python, or would otherwise consider themselves a python
beginner, please consider asking questions on the `r/learnpython
<https://www.reddit.com/r/learnpython>`_ subreddit. There are wonderful people
there who can help with general python and simple PRAW related questions.

Otherwise, there are a few official places to ask questions about PRAW:

`/r/redditdev <https://www.reddit.com/r/redditdev>`_ is the best place on
reddit to ask PRAW related questions. This subreddit is for all reddit API
related discussion so please tag submissions with *[PRAW4]*. Please perform a
search on the subreddit first to see if anyone has similar questions.

Real-time chat can be conducted via the `praw-dev/praw
<https://gitter.im/praw-dev/praw>`_ channel on gitter.

Please do not directly message any of the contributors via reddit, email, or
gitter unless they have indicated otherwise. We strongly encourage everyone to
help others with their questions.

Please file bugs and feature requests as issues on `GitHub
<https://github.com/praw-dev/praw/issues>`_ after first searching to ensure a
similar issue was not already filed. If such an issue already exists please
give it a thumbs up reaction. Comments to issues containing additional
information are certainly welcome.

.. note:: This project is released with a `Contributor Code of Conduct
   <https://github.com/praw-dev/praw/blob/praw4/CODE_OF_CONDUCT.md>`_. By
   participating in this project you agree to abide by its terms.

Documentation
-------------

PRAW's documentation is located at https://praw.readthedocs.io.

.. note:: At this time the majority of the documentation has not yet been
   updated to PRAW4. Contributions are welcome.

License
-------

`GPLv3 <https://github.com/praw-dev/praw/blob/praw4/COPYING>`_

Donations
---------

Please consider donating to PRAW's maintainer via https://cash.me/$praw.
