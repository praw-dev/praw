Quick Start
===========
In this section, we are going over everything you need to know to start
building bots using Python Reddit API Wrapper (PRAW). It's fun and easy. Let's
get started.

Prerequisites
*************

- **Python**: Obviously, you need to know at least a little Python to use PRAW;
  it's a Python wrapper after all. PRAW supports `Python 2.7`_, and `Python 3.3
  to 3.5`_. If you are stuck on a problem, `/r/learnpython`_ is a a great place
  to get help.

.. _`Python 2.7`: https://docs.python.org/2/tutorial/index.html
.. _`Python 3.3 to 3.5`: https://docs.python.org/3/tutorial/index.html
.. _`/r/learnpython`: https://www.reddit.com/r/learnpython/

- **reddit**: A basic understanding of how reddit.com works is a must, although
  we can safely assume that a person who is reading the documentation of a
  reddit API wrapper must have that covered. Just in case you don't, here is
  the FAQ_.

You would also need a reddit account to register apps with reddit before you
can use their API through PRAW.

.. _FAQ: https://www.reddit.com/wiki/faq

- **user-agent**: A user-agent is a string that helps the reddit server
  identify the source of the requests. To use reddit API, you need a unique and
  descriptive user-agent string. The recommended format is ``<platform>:<app
  ID>:<version string> (by /u/<reddit username>)``. For example,
  ``android:com.example.myredditapp:v1.2.3 (by /u/kemitche)``. Read more about
  user-agent strings on `reddit API's wiki page`_.

.. _`reddit API's wiki page`: https://github.com/reddit/reddit/wiki/API

- **client ID & client secret**: These two are also mandatory for PRAW4. If you
  don't already have them, follow the "First Steps" section on `this reddit API
  wiki page`_.

.. _`this reddit API wiki page`:
   https://github.com/reddit/reddit/wiki/OAuth2-Quick-Start-Example

That's pretty much it! You are ready to learn how to do some of the most common
tasks of reddit bot building!

Common Tasks
************

Obtain a ``Reddit`` instance
----------------------------

You need an instance of the ``Reddit`` class to do *anything* with PRAW. And
there are "two kinds" of ``Reddit`` instance you can create, the read-only one
and the regular one. They differ in the amount of settings information needed.

The read-only ``Reddit`` instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create a read-only ``Reddit`` instance, you need three pieces of settings
information:

1) user agent
2) client ID
3) client secret

You may choose to provide these by passing in three key-word arguments when
calling the initializer of the ``Reddit`` class: ``user_agent``, ``client_id``,
and ``client_secret``. For example:

.. code-block:: python

    import praw

    my_user_agent = "my user agent"
    my_client_id = "my client ID"
    my_client_secret = "my client secret"

    reddit = praw.Reddit(user_agent=my_user_agent,
                         client_id=my_client_id,
                         client_secret=my_client_secret)

Just like that, now you've got a Reddit instance. Keep in mind though, this
instance is in *read-only* mode.

.. code-block:: python

    print(reddit.read_only) # Output: True

You can do limited (read-only) things with this instance like "getting 10
'hot' submissions of the 'learnpython' subreddit":

.. code-block:: python

   # continue from code above

   for submission in reddit.subreddit('learnpython').hot(limit=10):
       print(submission.title)

   # Output: 10 submission

You can do some things with a read-only instance, but not a lot. In most cases
you would need a regular instance.

The regular ``Reddit`` instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to create a regular ``Reddit`` instance, two additional pieces of
settings information is required:

4) your reddit user name, and
5) your reddit password

Again, you may choose to provide these by passing in key-word arguments,
``username`` and ``password``, when you call the ``Reddit`` initializer, like
this:

.. code-block:: python

   import praw

   my_user_agent = "my user agent"
   my_client_id = "my client ID"
   my_client_secret = "my client secret"
   my_username = "my username"
   my_password = "my password"

   reddit = praw.Reddit(user_agent=my_user_agent,
                        client_id=my_client_id,
                        client_secret=my_client_secret,
                        username=my_username,
                        password=my_password)

   print(reddit.read_only) # Output: False

Now you can do whatever your reddit account is authorized to do. And you can
switch back to read-only mode whenever you want:

.. code-block:: python

   # continue from code above
   reddit.read_only = True

Nonetheless, if you are uncomfortable of hard coding your credentials, we have
two other options for you.

Providing Configuration Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We have learned that five pieces of settings information are needed in order
to create a regular ``Reddit`` instance:

1) user agent
2) client ID
3) client secret
4) your reddit user name
5) your reddit password

And we have been passing these as key-word arguments to the ``Reddit``
initializer. If you look at the source, however, you may notice that the
``Reddit`` initializer does not directly ask for any of these parameters.  They
are all passed along when creating a ``Config`` instance.

So what happens if you don't pass any arguments when calling ``Reddit()``?
Then the ``Config`` class will look for those settings in two locations in the
following order of priority:

1) environment variables of the settings names prefixed with ``praw_``.
   Specifically, these:

   - ``praw_user_agent``
   - ``praw_client_id``
   - ``praw_client_secret``
   - ``praw_username``
   - ``praw_password``

   For example, you can invoke your script like this:

.. code-block:: shell

   praw_username=bboe praw_password=not_my_password python my_script.py

2) in the ``praw.ini`` file you provide. The section name for these settings
   should be specified with an environment variable named ``praw_site``; if no
   such environment variable is set, the default section name is ``DEFAULT``.
   You can put your ``praw.ini`` file in one or both of the following places
   (both will be read if present):

   1. the working directory when you invoke your script
   2. your OS's config directory (for Linux, this is ``$XDG_CONFIG_HOME`` or
      ``$HOME/.config``; for Windows, this is ``${APPDATA}``)

   If you don't know how to write ini files, follow `this example`_.

.. _`this example`: https://github.com/praw-dev/praw/blob/praw4/praw/praw.ini

Get a subreddit
---------------

To get a ``Subreddit`` instance, all you need to know is the subreddit's
display name. Pass that name when calling the ``subreddit`` method of your
``Reddit`` instance. For example:

.. code-block:: python

   # assuming you have a Reddit instance referenced by reddit
   subreddit = reddit.subreddit("redditdev")

   print(subreddit.display_name) # Output: redditdev
   print(subreddit.title) # Output: reddit Development
   print(subreddit.description) # Output: A subreddit for discussion of ...

Get submissions from a subreddit
--------------------------------

Now that you have a ``Subreddit`` instance, you can get some submissions
(``Submission`` instances) from it! There are several ways of sorting all the
submissions of a subreddit: hot, new, top, etc. A ``Subreddit`` instance has a
method for each of these sorting approaches, namely, these:

    ``controversial``
    ``gilded``
    ``hot``
    ``new``
    ``rising``
    ``top``

.. _submission-iteration:

Each of these methods will return ``ListingGenerator``, something that you can
iterate through. For example:

.. code-block:: python

   # assuming you have a Subreddit instance referenced by subreddit
   for submission in subreddit.hot(limit=10):
       print(submission.title) # Output: the title of the submission
       print(submission.ups)   # Output: upvote count
       print(submission.id)    # Output: the ID of the submission
       print(submission.url)   # Output: the URL the submission points to
                               # or the the submission URL if it's a self post


You can create ``Submission`` instances in other ways too:

.. code-block:: python

   # assuming you have a Reddit instance referenced by reddit
   submission = reddit.submission(id="39zje0")
   print(submission.title) # Output: reddit will soon only be available ...

   # or
   submission = reddit.submission(url="https://www.reddit.com/...")


Get redditors
-------------

There are several ways to get a redditor (a ``Redditor`` instance), two of the
most common ones are:

    - via the ``author`` attribute of a ``Submission`` instance
    - call the ``redditor`` method on a ``Reddit`` instance

For example:

.. code-block:: python

   # assuming you have a Reddit instance referenced by reddit
   # assuming you have a Submission instance referenced by submission
   redditor1 = submission.author
   print(redditor1.name) # Output: name of the redditor

   redditor2 = reddit.redditor('bboe')
   print(redditor2.link_karma) # Output: bboe's karma

Get comments
------------

Submissions have a ``comments`` attribute that is a ``CommentForest``
instance. That instance is iterable and represents the top-level comments.  If
you instead want to iterate over *all* comments you can get a list of comments
via the ``list`` method of a ``CommentForest`` instance. For example:

.. code-block:: python

   # assuming you have a Reddit instance referenced by reddit
   # assuming you have a Submission instance referenced by submission
   top_level_comments = list(submission.comments)
   all_comments = submission.comments.list()

As you may be aware there will periodically be ``MoreComments`` instances
scattered throughout the forest. Replace those at any time by calling the
``replace_more`` method on the ``CommentForest`` instances.

Get available attributes of an object
-------------------------------------

If you have a PRAW object, be it ``Submission`` or ``Comment``, and you want to
see what attributes are available and their values, use the built-in ``vars``
function of python. For example:

.. code-block:: python

   import pprint

   # assuming you have a Reddit instance referenced by reddit
   submission = reddit.submission(id="39zje0")
   print(submission.title) # to make it non-lazy
   pprint.pprint(vars(submission))

Note the line where we print the title. PRAW uses lazy objects to only make API
calls when/if the information is needed. Here, before the print line,
``submission`` points to a lazy ``Submission`` object. When we try to print its
title, information is needed, so it ceased to be lazy -- PRAW makes the actual
API call at this point. Now it is a good time to print out all the available
attributes and their values!
