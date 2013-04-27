.. _multiprocess:

Concurrent PRAW Instances
=========================

By default, PRAW works great when there is a one-to-one mapping between running
PRAW processes, and the IP address / user account that you make requests
from. In fact, as of version 2.1.0, PRAW has multithreaded support as long as
there is a one-to-one mapping between thread and PRAW :class:`.Reddit` object
instance. That is, in order to be thread safe, each thread needs to have its
own :class:`.Reddit` instance [#]_. In addition to multithreaded rate-limiting
support, PRAW 2.1.0 added multiprocess rate limiting support.

.. [#] It is undetermined at this time if the same authentication credentials
    can be used on multiple instances where the modhash is concerned.


praw-multiprocess
-----------------

PRAW version 2.1.0 and later install with a program **praw-multiprocess**. This
program provides a request handling server that manages the rate-limiting and
caching of any PRAW process which directs requests toward it. Starting
**praw-multiprocess** is as simple as running ``praw-multiprocess`` from your
terminal / command line assuming you :ref:`installed PRAW <installation>`
properly.

By default **praw-multiprocess** will listen only on *localhost* port
*10101*. You can adjust those settings by passing in ``--addr`` and ``--port``
arguments respectively. For instance to have **praw-multiprocess** listen on
all valid addresses on port 65000, execute via: ``praw-multiprocess --addr
0.0.0.0 --port 65000``. For a full list of options execute ``praw-multiprocess
--help``.


PRAW's MultiprocessingHandler
-----------------------------

In order to interact with a **praw-multiprocess** server, PRAW needs to be
instructed to use the :class:`.MultiprocessHandler` rather than the
:class:`.DefaultHandler`. In your program you need to pass an instance of
:class:`.MultiprocessHandler` into the ``handler`` keyword argument when
creating the :class:`.Reddit` instance. Below is an example to connect to a
**praw-multiprocess** server running with the default arguments:

.. code-block:: python

    import praw
    from praw.handlers import MultiprocessHandler

    handler = MultiprocessHandler()
    r = praw.Reddit(user_agent='a descriptive user agent', handler=handler)

With this configuration, all network requests made from your program(s) that
include the above code will be *proxied* through the `praw-multiprocess`
server. All requests made through the same **praw-multiprocess** server will
respect reddit's API rate-limiting rules

If instead, you wish to connect to a **praw-multiprocess** server running at
address ``10.0.0.1`` port 65000 then you would create the PRAW instance via:

.. code-block:: python

    import praw
    from praw.handlers import MultiprocessHandler

    handler = MultiprocessHandler('10.0.0.1', 65000)
    r = praw.Reddit(user_agent='a descriptive user agent', handler=handler)


PRAW Multiprocess Resiliency
----------------------------

With all client/server type programs there is the possibility of network issues
or simply a lack of an available server. PRAW's :class:`.MultiprocessHandler`
was created to be quite resilient to such issues. PRAW will retry indefinitely
to connect to **praw-multiprocess** server. This means that a
**praw-multiprocess** server can be stopped and restarted without any effect on
programs utilizing it.

On the other hand, consecutive network failures where the
:class:`.MultiprocessHandler` has no issue establishing a connection to a
**praw-multiprocess** server will result in :class:`.ClientException` after
three failures. Such failures are **not** expected to occur and if
reproducable should be :ref:`reported <report_an_issue>`.
