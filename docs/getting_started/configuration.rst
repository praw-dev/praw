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

Environment variables have the highest priority, followed by keyword arguments to
:class:`.Reddit`, and finally settings in ``praw.ini`` files.

Using an HTTP or HTTPS proxy with PRAW
--------------------------------------

PRAW internally relies upon the `requests <https://requests.readthedocs.io/>`_ package
to handle HTTP requests. Requests supports use of ``HTTP_PROXY`` and ``HTTPS_PROXY``
environment variables in order to proxy HTTP and HTTPS requests respectively [`ref
<https://requests.readthedocs.io/en/master/user/advanced/#proxies>`_].

Given that PRAW exclusively communicates with Reddit via HTTPS, only the ``HTTPS_PROXY``
option should be required.

For example, if you have a script named ``prawbot.py``, the ``HTTPS_PROXY`` environment
variable can be provided on the command line like so:

.. code-block:: bash

    HTTPS_PROXY=http://localhost:3128 ./prawbot.py


Configuring a custom requests Session
-------------------------------------

PRAW uses `requests`_ to handle networking. If your use-case requires custom
configuration, it is possible to configure a `Session
<https://requests.readthedocs.io/en/master/user/advanced/#session-objects>`_ and then
use it with PRAW.

For example, some networks use self-signed SSL certificates when connecting to HTTPS
sites. By default, this would raise an exception in Requests. To use a self-signed SSL
certificate without an exception from Requests, first export the certificate as a
``.pem`` file. Then configure PRAW like so:

.. code-block:: python

    import praw
    from requests import Session


    session = Session()
    session.verify = "/path/to/certfile.pem"
    reddit = praw.Reddit(client_id="SI8pN3DSbt0zor",
        client_secret="xaxkj7HNh8kwg8e5t4m6KvSrbTI",
        password="1guiwevlfo00esyy",
        requestor_kwargs={"session": session},  # pass Session
        user_agent="testscript by u/fakebot3",
        username="fakebot3"
    )


The code above creates a Session and `configures it to use a custom certificate
<https://requests.readthedocs .io/en/master/user/advanced/#ssl-cert-verification>`_,
then passes it as a parameter when creating the :class:`.Reddit` instance. Note that the
example above uses a :ref:`password_flow` authentication type, but this method will work
for any authentication type.
