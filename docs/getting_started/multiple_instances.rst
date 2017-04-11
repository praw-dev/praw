Running Multiple Instances of PRAW
==================================

PRAW, as of version 4, performs rate limiting dynamically based on the HTTP
response headers from Reddit. As a result you can safely run a handful of PRAW
instances without any additional configuration.

.. note:: Running more than a dozen or so instances of PRAW concurrently from
          may occasionally result in exceeding Reddit's rate limits as each
          instance can only guess how many other instances are running.

If you are authorized on other users behalf, each authorization should have its
own rate limit, even when running from a single IP address.

Multiple Programs
-----------------

The recommended way to run multiple instances of PRAW is to simply write
separate independent python programs. With this approach one program can
monitor a comment stream and reply as needed, and another program can monitor a
submission stream, for example.

If these programs need to share data consider using a third party system such
as a database, or queuing system.

Multiple Threads
----------------

.. warning:: PRAW is not thread safe.

In a nutshell, instances of :class:`.Reddit` are not thread safe for a number
of reasons in its own code and each instance depends on an instance of
``requests.Session``, which is not thread safe [`ref
<https://github.com/kennethreitz/requests/issues/2766>`_].

In theory having a unique :class:`.Reddit` instance for each thread should
work. However, until someone perpetually volunteers to be PRAW's thread safety
instructor, little to no support will go toward any PRAW issues that could be
affected by the use of multiple threads. Consider using multiple processes
instead.

Please see `this discussion
<https://www.reddit.com/r/redditdev/comments/5uwxke/praw4_is_praw4_thread_safe/>`_
for more information.
