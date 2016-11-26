.. _configuration:

Configuring PRAW
================

.. toctree::
   :maxdepth: 2

   configuration/options


Configuration options can be provided to PRAW in one of three ways:

.. toctree::
   :maxdepth: 1

   configuration/prawini
   configuration/reddit_initialization
   configuration/environment_variables

Environment variables have the highest priority, followed by keyword arguments
to :class:`.Reddit`, and finally settings in ``praw.ini`` files.

Using an HTTP or HTTPS proxy with PRAW
--------------------------------------

PRAW internally relies upon the `requests <http://docs.python-requests.org/>`_
package to handle HTTP requests. Requests supports use of ``HTTP_PROXY`` and
``HTTPS_PROXY`` environment variables in order to proxy HTTP and HTTPS requests
respectively [`ref
<http://docs.python-requests.org/en/master/user/advanced/#proxies>`_].

Given that PRAW exclusively communicates with Reddit via HTTPS, only the
``HTTPS_PROXY`` option should be required.

For example, if you have a script named ``prawbot.py``, the ``HTTPS_PROXY``
environment variable can be provided on the command line like so:

.. code-block:: bash

   HTTPS_PROXY=https://localhost:3128 ./prawbot.py
