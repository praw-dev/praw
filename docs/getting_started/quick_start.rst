Quick Start
===========
In this section, we are going over everything you need to know to start
building bots using Python Reddit API Wrapper (PRAW). It's fun and easy. Let's
get started.

Prerequisites
-------------

:Python: Obviously, you need to know at least a little Python to use PRAW; it's
         a Python wrapper after all. PRAW supports `Python 2.7`_, and `Python
         3.3 to 3.5`_. If you are stuck on a problem, `/r/learnpython`_ is a a
         great place to get help.

.. _`Python 2.7`: https://docs.python.org/2/tutorial/index.html
.. _`Python 3.3 to 3.5`: https://docs.python.org/3/tutorial/index.html
.. _`/r/learnpython`: https://www.reddit.com/r/learnpython/

:Reddit: A basic understanding of how `reddit.com`_ works is a must, although
         we can safely assume that a person who is reading the documentation of
         a Reddit API wrapper must have that covered. Just in case you don't,
         here is the FAQ_.

You would also need a Reddit account to register apps with Reddit before you
can use their API through PRAW.

.. _reddit.com: https://www.reddit.com
.. _FAQ: https://www.reddit.com/wiki/faq

:user-agent: A user-agent is a string that helps the Reddit server identify the
             source of the requests. To use Reddit's API, you need a unique and
             descriptive user-agent string. The recommended format is
             ``<platform>:<app ID>:<version string> (by /u/<Reddit
             username>)``. For example,
             ``android:com.example.myredditapp:v1.2.3 (by /u/kemitche)``. Read
             more about user-agent strings on `Reddit's API wiki page`_.

.. _`Reddit's API wiki page`: https://github.com/reddit/reddit/wiki/API

:client ID & client secret: These two values are mandatory for PRAW. If you
                            don't already have them check out follow Redddit's
                            `First Steps Guide`_ and then continue below.

.. _`First Steps Guide`:
   https://github.com/reddit/reddit/wiki/OAuth2-Quick-Start-Example#first-steps

That's pretty much it! You are ready to learn how to do some of the most common
tasks of Reddit bot building!

Common Tasks
------------

Obtain a :class:`.Reddit` Instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need an instance of the :class:`.Reddit` class to do *anything* with
PRAW. There are two distinct states a :class:`.Reddit` instance can be in:
read-only, and authorized.

Read-only :class:`.Reddit` Instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create a read-only :class:`.Reddit` instance, you need three pieces of
settings information:

1) user agent
2) client ID
3) client secret

You may choose to provide these by passing in three key-word arguments when
calling the initializer of the :class:`.Reddit` class: ``user_agent``,
``client_id``, and ``client_secret``. For example:

.. code-block:: python

   import praw

   my_user_agent = 'my user agent'
   my_client_id = 'my client ID'
   my_client_secret = 'my client secret'

   reddit = praw.Reddit(user_agent=my_user_agent,
                        client_id=my_client_id,
                        client_secret=my_client_secret)

Just like that, you now have a read-only  :class:`.Reddit` instance.

.. code-block:: python

   print(reddit.read_only)  # Output: True

You can do limited (read-only) things with this instance like "obtaining 10
'hot' submissions of the 'learnpython' subreddit":

.. code-block:: python

   # continued from code above

   for submission in reddit.subreddit('learnpython').hot(limit=10):
       print(submission.title)

   # Output: 10 submission

You can do some things with a read-only instance, but not a lot. In most cases
you need an authorized :class:`.Reddit` instance.

Authorized :class:`.Reddit` Instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to create an authorized :class:`.Reddit` instance, two additional
pieces of information are required:

4) your Reddit user name, and
5) your Reddit password

Again, you may choose to provide these by passing in key-word arguments,
``username`` and ``password``, when you call the :class:`.Reddit` initializer,
like this:

.. code-block:: python

   import praw

   my_user_agent = 'my user agent'
   my_client_id = 'my client ID'
   my_client_secret = 'my client secret'
   my_username = 'my username'
   my_password = 'my password'

   reddit = praw.Reddit(user_agent=my_user_agent,
                        client_id=my_client_id,
                        client_secret=my_client_secret,
                        username=my_username,
                        password=my_password)

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

To obtain a :class:`.Subreddit` instance, all you need to know is the
subreddit's display name. Pass that name when calling ``subreddit`` on
your :class:`.Reddit` instance. For example:

.. code-block:: python

   # assume you have a Reddit instance bound to variable `reddit`
   subreddit = reddit.subreddit('redditdev')

   print(subreddit.display_name) # Output: redditdev
   print(subreddit.title) # Output: reddit Development
   print(subreddit.description) # Output: A subreddit for discussion of ...

Obtain :class:`.Submission` Instances from a :class:`.Subreddit`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that you have a :class:`.Subreddit` instance, you can obtain some
submissions (:class:`.Submission` instances) from it! There are several ways of
sorting all the submissions of a subreddit: hot, new, top, etc. A
:class:`.Subreddit` instance has a method for each of these sorting approaches,
namely, these:

- controversial
- gilded
- hot
- new
- rising
- top

.. _submission-iteration:

Each of these methods will immediately return a :class:`.ListingGenerator`,
which is something that you can iterate through. For example:

.. code-block:: python

   # assume you have a Subreddit instance bound to variable `subreddit`
   for submission in subreddit.hot(limit=10):
       print(submission.title)  # Output: the title of the submission
       print(submission.ups)    # Output: upvote count
       print(submission.id)     # Output: the ID of the submission
       print(submission.url)    # Output: the URL the submission points to
                                # or the the submission URL if it's a self post

.. note:: The act of calling a method that returns a :class:`.ListingGenerator`
          does not result in any network requests until you begin to iterate
          through the :class:`.ListingGenerator`.

You can create :class:`.Submission` instances in other ways too:

.. code-block:: python

   # assume you have a Reddit instance bound to variable `reddit`
   submission = reddit.submission(id='39zje0')
   print(submission.title) # Output: reddit will soon only be available ...

   # or
   submission = reddit.submission(url='https://www.reddit.com/...')


Obtain :class:`.Redditor` Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are several ways to obtain a redditor (a :class:`.Redditor` instance),
two of the most common ones are:

- via the ``author`` attribute of a :class:`.Submission` or :class:`.Comment`
  instance
- via the :meth:`.redditor` method of :class:`.Reddit`

For example:

.. code-block:: python

   # assume you have a Reddit instance bound to variable `reddit`
   # assume you have a Submission instance bound to variable `submission`
   redditor1 = submission.author
   print(redditor1.name) # Output: name of the redditor

   redditor2 = reddit.redditor('bboe')
   print(redditor2.link_karma) # Output: bboe's karma

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

If you have a PRAW object, be it :class:`.Submission` or :class:`.Comment`, and
you want to see what attributes are available and their values, use the
built-in ``vars`` function of python. For example:

.. code-block:: python

   import pprint

   # assume you have a Reddit instance bound to variable `reddit`
   submission = reddit.submission(id='39zje0')
   print(submission.title) # to make it non-lazy
   pprint.pprint(vars(submission))

Note the line where we print the title. PRAW uses lazy objects to only make API
calls when the information is needed. Here, before the print line,
``submission`` points to a lazy :class:`.Submission` object. When we try to
print its title, information is needed, so it ceased to be lazy -- PRAW makes
the actual API call at this point. Now it is a good time to print out all the
available attributes and their values!
