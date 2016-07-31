Getting Started
===============

The following material will help you get started with PRAW:

.. toctree::
   :maxdepth: 1

   reply_bot


.. _submission-iteration:

Iterating Over Submissions
--------------------------

There are two primary methods for iterating through submissions.

The first method is to pick a subreddit, and then iterate through one of its
many generators of submissions, e.g., ``hot``, ``new``, or ``top``. In the
following example we build a list of submissions which may be used for later
processing.

.. code-block:: python

   submissions = []
   for submission in reddit.subreddit('python').hot():
       submissions.append(submission)

.. note:: Just like on the website, multiple subreddits can be specified by
   joining them with a plus (`+`), e.g., ``python+redditdev``.

The second method is to iterate over submissions from a subreddit's submission
stream (:meth:`praw.models.reddit.subreddit.SubredditStream.submissions`). A
submission stream indefinitely yields new submissions as they are made to
Reddit. For example:

.. code-block:: python

   subreddit = reddit.subreddit('python')
   for submission in subreddit.stream.submissions():
       print(submission.selftext)

The ``selftext`` attribute of a :class:`.Submission` contains the markdown
formatted text of a *self* type submission. For a complete list of attributes,
and their values, available on a PRAW object try the following:

.. code-block:: python

   from pprint import pprint
   pprint(vars(submission))

.. note:: ``vars`` can be used on instances of almost all classes in python,
   and can be useful in any python project.
