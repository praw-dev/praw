Comment Extraction and Parsing
==============================

A common use for Reddit's API is to extract comments from submissions and use
them to perform keyword or phrase analysis.

As always, you need to begin by creating an instance of :class:`.Reddit`:

.. code-block:: python

   import praw

   reddit = praw.Reddit(user_agent='Comment Extraction (by /u/USERNAME)',
                        client_id='CLIENT_ID', client_secret="CLIENT_SECRET",
                        username='USERNAME', password='PASSWORD')

.. note:: If you are only analyzing public comments, entering a username and
   password is optional.

In this document we will detail the process of finding all the comments for a
given submission. If you instead want process all comments on Reddit, or
comments belonging to one or more specific subreddits, please see
:meth:`praw.models.reddit.subreddit.SubredditStream.comments`.

.. _extracting_comments:

Extracting comments with PRAW
-----------------------------

Assume we want to process the comments for this submission:
https://www.reddit.com/r/funny/comments/3g1jfi/buttons/

We first need to obtain a submission object. We can do that either with the
entire URL:

.. code-block:: python

   submission = reddit.submission(url='https://www.reddit.com/r/funny/comments/3g1jfi/buttons/')

or with the submission's ID which comes after `comments/` in the URL:

.. code-block:: python

   submission = reddit.submission(id='3g1jfi')

With a submission object we can then interact with its :class:`.CommentForest`
through the submission's :attr:`~praw.models.Submission.comments` attribute. A
:class:`.CommentForest` is a list of top-level comments each of which contains
a :class:`.CommentForest` of replies.

If we wanted to output only the ``body`` of the top level comments in the
thread we could do:

.. code-block:: python

   for top_level_comment in submission.comments:
       print(top_level_comment.body)

While running this you will most likely encounter the exception
``AttributeError: 'MoreComments' object has no attribute 'body'``. This
submission's comment forest contains a number of :class:`.MoreComments`
objects. These objects represent the "load more comments", and "continue this
thread" links encountered on the website. While we could ignore
:class:`.MoreComments` in our code, like so:

.. code-block:: python

   from praw.models import MoreComments
   for top_level_comment in submission.comments:
       if isinstance(top_level_comment, MoreComments):
           continue
       print(top_level_comment.body)

The preferred way is to use the :meth:`.replace_more` method of the
:class:`.CommentForest`. Calling :meth:`.replace_more` will replace or remove
all the :class:`.MoreComments` objects in the comment forest. Each replacement
requires one network request, and its response may yield additional
:class:`.MoreComments` instances. As a result, by default,
:meth:`.replace_more` only replaces at most thirty-two :class:`.MoreComments`
instances -- all other instances are simply removed. The maximum number of
instances to replace can be configured via the ``limit`` paramter. Additionally
a ``threshold`` parameter can be set to only perform replacement of
:class:`.MoreComments` instances that represent a minimum number of comments;
it defaults to 0, meaning all :class:`.MoreComments` instances will be replaced
up to ``limit``.

We can rewrite the snippet above as the following, which simply removes all
:class:`.MoreComments` instances from the comment forest:

.. code-block:: python

   submission.comments.replace_more(limit=0)
   for top_level_comment in submission.comments:
       print(top_level_comment.body)

.. note:: Calling :meth:`.replace_more` is destructive. Calling it again on the
   same submission instance has no effect.

Now we are able to successfully iterate over all the top-level comments. What
about their replies? We could output all second-level comments like so:

.. code-block:: python

   submission.comments.replace_more(limit=0)
   for top_level_comment in submission.comments:
       for second_level_comment in top_level_comment.replies:
           print(second_level_comment.body)

However, the comment forest can be arbitrarily deep, so we'll want a more
robust solution. One way to iterate over a tree, or forest, is via a
breath-first traversal using a queue:

.. code-block:: python

   submission.comments.replace_more(limit=0)
   comment_queue = submission.comments[:]  # Seed with top-level
   while comment_queue:
       comment = comment_queue.pop(0)
       print(comment.body)
       comment_queue.extend(comment.replies)

The above code will output all the top-level comments, followed, by
second-level, third-level, etc. While it is awesome to be able to do your own
breadth-first traversals, :class:`.CommentForest` provides a convenience
method, :meth:`.list`, which returns a list of comments traversed in the same
order as the code above. Thus the above can be rewritten as:

.. code-block:: python

   submission.comments.replace_more(limit=0)
   for comment in submission.comments.list():
       print(comment.body)

Now you can now properly extract and parse all (or most) of the comments
belonging to a single submission. Combine this with :ref:`submission iteration
<submission-iteration>` and you can build some really cool stuff.

Finally, note that the value of ``submission.num_comments`` may not match up
100% with the number of comments extracted via PRAW. This discrepancy is
normal as that count includes deleted, removed, and spam comments.
