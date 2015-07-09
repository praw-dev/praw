.. _exceptions:

Exceptions
==========

This page documents the exceptions that can occur while running PRAW and what
they mean. The exceptions can be divided into three rough categories and a full
list of the ``ClientException`` s and ``APIException`` s that can occur can be
found in the `errors module
<https://praw.readthedocs.org/en/latest/pages/code_overview.html
#module-praw.errors>`_.

ClientException
---------------

Something went wrong on the client side of the request. All exceptions of this
nature inherit from the exception class ``ClientException``. Most of these
exceptions occur when you try to do something you don't have authorization to
do. For instance trying to remove a submission in a subreddit where the
logged-in user is not a moderator will throw a ``ModeratorRequired`` error.


APIException
------------

Something went wrong on the server side of the request. All exceptions of this
nature inherit from the exception class ``APIException``. They deal with all
sorts of errors that can occur when communicating with a remote API such as
trying to login with the incorrect password, which raise a ``InvalidUserPass``.


HTTPException
-------------

All other errors. The most common occurrence is when reddit returns a non-200
status code. This will raise an exception that is either an object of the
:class:`.HTTPException` or one of its subclasses.

Each of these exceptions will likely have an associated HTTP response status
code. The meanings of some of these status codes are:

301, 302
^^^^^^^^

Redirects. Are automatically handled in PRAW, but may result in a
``RedirectException`` if an unexpected redirect is encountered.

403 (:class:`.Forbidden`)
^^^^^^^^^^^^^^^^^^^^^^^^

This will occur if you try to access a restricted resource. For instance a
private subreddit that the currently logged-in user doesn't have access to.

.. code-block:: pycon

    >>> import praw
    >>> r = praw.Reddit('404 test by u/_Daimon_')
    >>> r.get_subreddit('lounge', fetch=True)

404 (:class:`.NotFound`)
^^^^^^^^^^^^^^^^^^^^^^^^

Indicates that the requested resource does not exist.

500
^^^

An internal error happened on the server. Sometimes there's a temporary hiccup
that cause this and repeating the request will not re-raise the issue. If it's
consistently thrown when you call the same PRAW method with the same arguments,
then there's either a bug in the way PRAW parses arguments or in the way reddit
handles them. Create a submission on `r/redditdev
<http://www.reddit.com/r/redditdev>`_ so that the right people become aware of
the issue and can solve it.

502, 503, 504
^^^^^^^^^^^^^

A temporary issue at reddit's end. Usually only happens when the servers are
under very heavy pressure. Since it's a temporary issue, PRAW will
automatically retry the request for you. If you're seeing this error then PRAW
has either failed with this request 3 times in a row or it's a request that
adds something to reddit's database like
:meth:`~praw.objects.Submission.add_comment`. In this case, the error may be
thrown after the comment was added to reddit's database, so retrying the
request could result in duplicate comments. To prevent duplication such
requests are not retried on errors.
