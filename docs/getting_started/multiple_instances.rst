Running Multiple Instances of PRAW
==================================

PRAW, as of version 4, performs rate limiting dynamically based on the HTTP response
headers from Reddit. As a result you can safely run a handful of PRAW instances without
any additional configuration.

.. note::

    Running more than a dozen or so instances of PRAW concurrently may occasionally
    result in exceeding Reddit's rate limits as each instance can only guess how many
    other instances are running.

If you are authorized on other users' behalf, each authorization should have its own
rate limit, even when running from a single IP address.

Discord Bots and Asynchronous Environments
------------------------------------------

If you plan on using PRAW in an asynchronous environment, (e.g., discord.py, asyncio) it
is strongly recommended to use `Async PRAW <https://asyncpraw.readthedocs.io/>`_. It is
the official asynchronous version of PRAW and its usage is similar and has the same
features as PRAW.

.. note::

    By default, PRAW will check to see if it is in an asynchronous environment every
    time a network request is made. To disable this check, set the ``check_for_async``
    configuration option to ``false``. For example:

    .. code-block:: python

        import praw

        reddit = praw.Reddit(..., check_for_async=False)

Multiple Programs
-----------------

The recommended way to run multiple instances of PRAW is to simply write separate
independent Python programs. With this approach one program can monitor a comment stream
and reply as needed, and another program can monitor a submission stream, for example.

If these programs need to share data consider using a third-party system such as a
database or queuing system.

Multiple Threads
----------------

.. warning::

    PRAW is not thread safe.

In a nutshell, instances of :class:`.Reddit` are not thread-safe for a number of reasons
in its own code and each instance depends on an instance of ``requests.Session``, which
is not thread-safe [`ref <https://github.com/kennethreitz/requests/issues/2766>`_].

In theory, having a unique :class:`.Reddit` instance for each thread, and making sure
that the instances are used in their respective threads only, will work.
:class:`multiprocessing.Process` has been confirmed to work with PRAW, so that is a
viable choice as well. However, there are various errors with
:class:`multiprocessing.pool.Pool`, thus it is not supported by PRAW. Please use
``multiprocessing.pool.ThreadPool`` as an alternative to a process pool.

Please see `this discussion
<https://www.reddit.com/r/redditdev/comments/5uwxke/praw4_is_praw4_thread_safe/>`_ and
`this GitHub issue <https://github.com/praw-dev/praw/issues/1336>`_ for more
information.
