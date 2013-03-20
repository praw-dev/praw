.. _faq:

Frequently Asked Questions
==========================

This is a list of frequently asked questions and a description of non-obvious
behaviour in PRAW and reddit.

FAQ
---

How do I get a comment by ID?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have a permalink to a comment you can use get_submission on the
permalink, and then the first comment should be the desired one.

>>> s = r.get_submission('http://www.reddit.com/r/redditdev/comments/s3vcj/_/c4axeer')
>>> your_comment = s.comments[0]

I made a change, but it doesn't seem to have an effect?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PRAW follow the `api guidelines <https://github.com/reddit/reddit/wiki/API>`_
which require that pages not be requested more than every 30 seconds. To do
this PRAW has an internal cache, which stores results for 30 seconds and give
you the cached result if you request the same page within 30 seconds.

Some commands take a while. Why?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PRAW follow the `api guidelines <https://github.com/reddit/reddit/wiki/API>`_
which require a 2 second delay between each API call.

When I print a Comment only part of it is printed. How can I get the rest?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A :class:`.Comment` is an object which contain a number of attributes with
information about the object such as ``author``, ``body`` or ``created_utc``.
When you use ``print`` the object string (well unicode) representation of the
object is printed. Use ``vars`` to discover what attributes and their values an
object has, see :ref:`writing_a_bot` for more details.

Why does the karma change from run to run?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This inconsistency is due to `reddit's obfuscation
<http://ww.reddit.com/help/faqs/
help#Whydothenumberofvoteschangewhenyoureloadapage>`_ of the upvotes and
downvotes. The obfuscation is done to everything and everybody to thwart
potential cheaters. There's nothing we can do to prevent this.

Non-obvious behaviour and other need to know
--------------------------------------------

* All of the listings (list of stories on subreddit, etc.) are generators,
  *not* lists. If you need them to be lists, an easy way is to call ``list()``
  with your variable as the argument.
* The default limit for fetching Things is 25. You can change this with the
  ``limit`` param. If want as many Things as you can then set ``limit=None``.
* We can at most get 1000 results from every listing, this is an upstream
  limitation by reddit. There is nothing we can do to go past this
  limit.  But we may be able to get the results we want with the
  :meth:`~.UnauthenticatedReddit.search` method instead.
