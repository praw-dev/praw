.. _configuration:

Configuring PRAW
================

.. toctree::
   :maxdepth: 2

   configuration_options


Configuration options can be provided to PRAW in one of three ways:

* :ref:`praw.ini`
* :ref:`reddit_initialization`
* :ref:`environment_variables`

Environment variables have the highest priority, followed by keyword arguments
when initializing instances of :class:`.Reddit`, and finally settings in
``praw.ini`` files.

.. _praw.ini:

praw.ini Files
--------------

Blah

.. _reddit_initialization:

Keyword Arguments to :class:`.Reddit`
-------------------------------------

.. _environment_variables:

PRAW Environment Variables
--------------------------

Blah


Using an HTTP or HTTPS proxy with PRAW
--------------------------------------

PRAW internally relies upon the `requests <http://docs.python-requests.org/>`_
package to handle HTTP requests. Requests supports use of ``HTTP_PROXY`` and
``HTTPS_PROXY`` environment variables in order to proxy HTTP and HTTPS requests
respectively [`ref
<http://docs.python-requests.org/en/master/user/advanced/#proxies>`_].

Given that PRAW exclusively communicates with Reddit via HTTPS, only the
`HTTPS_PROXY` option should be required.

If you have a script named ``prawbot.py``, the ``HTTPS_PROXY`` environment
variable can be provided on the command line like so:

.. code-block:: bash

   HTTPS_PROXY=https://localhost:3128 ./prawbot.py
