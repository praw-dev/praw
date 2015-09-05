.. _faq:

Frequently Asked Questions
==========================

This is a list of frequently asked questions and a description of non-obvious
behavior in PRAW and reddit.

FAQ
---

How do I get a comment by ID?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have a permalink to a comment you can use get_submission on the
permalink, and then the first comment should be the desired one.

>>> s = r.get_submission('http://www.reddit.com/r/redditdev/comments/s3vcj/_/c4axeer')
>>> your_comment = s.comments[0]


.. _handling-captchas:

How can I handle captchas myself?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Normally, PRAW will automatically prompt for a response whenever a captcha is
required. This works great if you're interactively running a program on the
terminal, but may not be desired for other applications. In order to prevent
the automatic prompting for captchas, one must add
``raise_captcha_exception=True`` to the function call:

>>> r.submit('reddit_api_test', 'Test Submission', text='Failed Captcha Test',
... raise_captcha_exception=True)
Traceback (most recent call last):
...
praw.errors.InvalidCaptcha: `care to try these again?` on field `captcha`

With this added keyword, you program can catch the :class:`.InvalidCaptcha`
exception and obtain the ``captcha_id`` via ``response['captcha']`` of the
exception instance.

In order to manually pass the captcha response to the desired function you must
add a ``captcha`` keyword argument with a value of the following format:

.. code-block:: pycon

    {'iden' : 'the captcha id', 'captcha': 'the captcha response text'}

For instance if the solution to ``captcha_id``
``f7UdxDmAEMbyLrb5fRALWJWvI5RPgGve`` is ``FYEMHB`` then the above submission
can be made with the following call:

>>> captcha = {'iden': 'f7UdxDmAEMbyLrb5fRALWJWvI5RPgGve', 'captcha': 'FYEMHB'}
>>> r.submit('reddit_api_test', 'Test Submission', text='Failed Captcha Test',
... raise_captcha_exception=True, captcha=captcha)
<praw.objects.Submission object at 0x2b726d0>

Note that we still add ``raise_captcha_exception=True`` in case the provided
captcha is incorrect.

I made a change, but it doesn't seem to have an effect?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PRAW follows the `api guidelines <https://github.com/reddit/reddit/wiki/API>`_
which require that pages not be requested more than every 30 seconds. To do
this PRAW has an internal cache, which stores results for 30 seconds and give
you the cached result if you request the same page within 30 seconds.

Some commands take a while. Why?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PRAW follows the `api guidelines <https://github.com/reddit/reddit/wiki/API>`_
which require a 2 second delay between each API call via CookieAuth. If you
are exclusively using OAuth2, you are allowed to change this delay in your
``praw.ini`` file to be a 1 second delay. This will be the default once
CookieAuth is deprecated.

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
<https://www.reddit.com/wiki/faq#wiki_how_is_a_submission.27s_score_determined.3F>`_
of the upvotes and downvotes. The obfuscation is done to everything and
everybody to thwart potential cheaters. There's nothing we can do to prevent
this.

.. _report_an_issue:

How do I report an issue with PRAW?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you believe you found an issue with PRAW that you can reliably reproduce
please `file an issue on github
<https://github.com/praw-dev/praw/issues/new>`_.  When reporting an issue,
please note the version of PRAW you are using (``python -c 'import praw;
print(praw.__version__)'``), and provide the code necessary to reproduce the
issue. It is strongly suggested that you condense your code as much as
possible.

Alternatively, if you cannot reliably reproduce the error, or if you do not
wish to create a github account, you can make a submission on `/r/redditdev
<http://www.reddit.com/r/redditdev>`_.

Non-obvious behavior and other need to know
-------------------------------------------

* All of the listings (list of stories on subreddit, etc.) are generators,
  *not* lists. If you need them to be lists, an easy way is to call ``list()``
  with your variable as the argument.
* The default limit for fetching Things is your `reddit preferences default
  <https://www.reddit.com/prefs>`_, usually 25. You can change this with the
  ``limit`` param. If want as many Things as you can then set ``limit=None``.
* We can at most get 1000 results from every listing, this is an upstream
  limitation by reddit. There is nothing we can do to go past this
  limit.  But we may be able to get the results we want with the
  :meth:`~.UnauthenticatedReddit.search` method instead.
