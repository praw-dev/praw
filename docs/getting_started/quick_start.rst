Quick Start
===========

In this section, we go over everything you need to know to start building
scripts, or bots using PRAW, the Python Reddit API Wrapper. It's fun and
easy. Let's get started.

Prerequisites
-------------

:Python Knowledge: You need to know at least a little Python to use PRAW; it's
                   a Python wrapper after all. PRAW supports `Python 2.7`_, and
                   `Python 3.3 to 3.5`_. If you are stuck on a problem,
                   `/r/learnpython`_ is a great place to ask for help.

:Reddit Knowledge: A basic understanding of how `reddit.com`_ works is a
                   must. In the event you are not already familiar with Reddit
                   start with their FAQ_.

:Reddit Account: A Reddit account is required to access Reddit's API. Create
                 one at `reddit.com`_.

:Client ID & Client Secret: These two values are needed to access Reddit's API
                            as a **script** application (see :ref:`oauth` for
                            other application types). If you don't already have
                            a client ID and client secret, follow Redddit's
                            `First Steps Guide`_ to create them.

:User Agent: A user agent is a unique indentifer that helps Reddit determine
             the source of network requests. To use Reddit's API, you need a
             unique and descriptive user agent. The recommended format is
             ``<platform>:<app ID>:<version string> (by /u/<Reddit
             username>)``. For example,
             ``android:com.example.myredditapp:v1.2.3 (by /u/kemitche)``. Read
             more about user-agents at `Reddit's API wiki page`_.


.. _`Python 2.7`: https://docs.python.org/2/tutorial/index.html
.. _`Python 3.3 to 3.5`: https://docs.python.org/3/tutorial/index.html
.. _`/r/learnpython`: https://www.reddit.com/r/learnpython/
.. _reddit.com: https://www.reddit.com
.. _FAQ: https://www.reddit.com/wiki/faq
.. _`Reddit's API wiki page`: https://github.com/reddit/reddit/wiki/API

.. _`First Steps Guide`:
   https://github.com/reddit/reddit/wiki/OAuth2-Quick-Start-Example#first-steps

With these prerequisites satisifed, you are ready to learn how to do some of
the most common tasks with Reddit's API.

Common Tasks
------------

Obtain a :class:`.Reddit` Instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need an instance of the :class:`.Reddit` class to do *anything* with
PRAW. There are two distinct states a :class:`.Reddit` instance can be in:
:ref:`read-only <read-only>`, and :ref:`authorized <authorized>`.

.. _read-only:

Read-only :class:`.Reddit` Instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create a read-only :class:`.Reddit` instance, you need three pieces of
information:

1) client ID
2) client secret
3) user agent

You may choose to provide these by passing in three keyword arguments when
calling the initializer of the :class:`.Reddit` class: ``client_id``,
``client_secret``, ``user_agent`` (see :ref:`configuration` for other methods
of providing this information). For example:

.. code-block:: python

   import praw

   reddit = praw.Reddit(client_id='my client id',
                        client_secret='my client secret',
                        user_agent='my user agent')

Just like that, you now have a read-only  :class:`.Reddit` instance.

.. code-block:: python

   print(reddit.read_only)  # Output: True

With a read-only instance, you can do something like obtaining 10 'hot'
submissions from ``/r/learnpython``:

.. code-block:: python

   # continued from code above

   for submission in reddit.subreddit('learnpython').hot(limit=10):
       print(submission.title)

   # Output: 10 submission

If you want to do more than retrieve public information from Reddit, then you
need an authorized :class:`.Reddit` instance.

.. _authorized:

Authorized :class:`.Reddit` Instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to create an authorized :class:`.Reddit` instance, two additional
pieces of information are required for **script** applications (see
:ref:`oauth` for other application types):

4) your Reddit user name, and
5) your Reddit password

Again, you may choose to provide these by passing in keyword arguments
``username`` and ``password`` when you call the :class:`.Reddit` initializer,
like the following:

.. code-block:: python

   import praw

   reddit = praw.Reddit(client_id='my client id',
                        client_secret='my client secret',
                        user_agent='my user agent',
                        username='my username',
                        password='my password')

   print(reddit.read_only)  # Output: False

Now you can do whatever your Reddit account is authorized to do. And you can
switch back to read-only mode whenever you want:

.. code-block:: python

   # continued from code above
   reddit.read_only = True

.. note:: If you are uncomfortable hard coding your credentials into your
          program, there are some options available to you. Please see:
          :ref:`configuration`.

Obtain a :class:`.Subreddit`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To obtain a :class:`.Subreddit` instance, pass the subreddit's name when
calling ``subreddit`` on your :class:`.Reddit` instance. For example:

.. code-block:: python

   # assume you have a Reddit instance bound to variable `reddit`
   subreddit = reddit.subreddit('redditdev')

   print(subreddit.display_name)  # Output: redditdev
   print(subreddit.title)         # Output: reddit Development
   print(subreddit.description)   # Output: A subreddit for discussion of ...

Obtain :class:`.Submission` Instances from a :class:`.Subreddit`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that you have a :class:`.Subreddit` instance, you can iterate through some
of its submissions, each bound to an instance of :class:`.Submission`. There
are several sorts that you can iterate through:

- controversial
- gilded
- hot
- new
- rising
- top

.. _submission-iteration:

Each of these methods will immediately return a :class:`.ListingGenerator`,
which is to be iterated through. For example, to iterate through the first 10
submissions based on the ``hot`` sort for a given subreddit try:

.. code-block:: python

   # assume you have a Subreddit instance bound to variable `subreddit`
   for submission in subreddit.hot(limit=10):
       print(submission.title)  # Output: the submission's title
       print(submission.score)  # Output: the submission's score
       print(submission.id)     # Output: the submission's ID
       print(submission.url)    # Output: the URL the submission points to
                                # or the submission's URL if it's a self post

.. note:: The act of calling a method that returns a :class:`.ListingGenerator`
          does not result in any network requests until you begin to iterate
          through the :class:`.ListingGenerator`.

You can create :class:`.Submission` instances in other ways too:

.. code-block:: python

   # assume you have a Reddit instance bound to variable `reddit`
   submission = reddit.submission(id='39zje0')
   print(submission.title)  # Output: reddit will soon only be available ...

   # or
   submission = reddit.submission(url='https://www.reddit.com/...')


Obtain :class:`.Redditor` Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are several ways to obtain a redditor (a :class:`.Redditor` instance).
Two of the most common ones are:

- via the ``author`` attribute of a :class:`.Submission` or :class:`.Comment`
  instance
- via the :meth:`.redditor` method of :class:`.Reddit`

For example:

.. code-block:: python

    # assume you have a Submission instance bound to variable `submission`
   redditor1 = submission.author
   print(redditor1.name)  # Output: name of the redditor

  # assume you have a Reddit instance bound to variable `reddit`
   redditor2 = reddit.redditor('bboe')
   print(redditor2.link_karma)  # Output: bboe's karma

Obtain :class:`.Comment` Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Submissions have a ``comments`` attribute that is a :class:`.CommentForest`
instance. That instance is iterable and represents the top-level comments of
the submission by the default comment sort (``best``). If you instead want to
iterate over *all* comments as a flattened list you can call the :meth:`.list`
method on a :class:`.CommentForest` instance. For example:

.. code-block:: python

   # assume you have a Reddit instance bound to variable `reddit`
   top_level_comments = list(submission.comments)
   all_comments = submission.comments.list()

.. note:: The comment sort order can be changed by updating the value of
          ``comment_sort`` on the :class:`.Submission` instance prior to
          accessing ``comments`` (see: `/api/set_suggested_sort
          <https://www.reddit.com/dev/api#POST_api_set_suggested_sort>`_ for
          possible values). For example to have comments sorted by ``new`` try
          something like:

          .. code-block:: python

             # assume you have a Reddit instance bound to variable `reddit`
             submission = reddit.submission(id='39zje0')
             submission.comment_sort = 'new'
             top_level_comments = list(submission.comments)

As you may be aware there will periodically be :class:`.MoreComments` instances
scattered throughout the forest. Replace those :class:`.MoreComments` instances
at any time by calling :meth:`.replace_more` on a :class:`.CommentForest`
instance. See :ref:`extracting_comments` for an example.

Determine Available Attributes of an Object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have a PRAW object, e.g., :class:`.Comment`, :class:`.Message`,
:class:`.Redditor`, or :class:`.Submission`, and you want to see what
attributes are available along with their values, use the built-in
:py:func:`vars` function of python. For example:

.. code-block:: python

   import pprint

   # assume you have a Reddit instance bound to variable `reddit`
   submission = reddit.submission(id='39zje0')
   print(submission.title) # to make it non-lazy
   pprint.pprint(vars(submission))

Note the line where we print the title. PRAW uses lazy objects so that network
requests to Reddit's API are only issued when information is needed. Here,
before the print line, ``submission`` points to a lazy :class:`.Submission`
object. When we try to print its title, additional information is needed, thus
a network request is made, and the instances ceases to be lazy. Outputting all
the attributes of a lazy object will result in fewer attributes than expected.
