Comment extraction and parsing.rst
==================================

One of the most common uses for the Reddit API is to extract comments from threads or subreddits and use them for some sort of keyword or phrase analysis.

As always, you need to begin by creating an instance of :class:`.Reddit`:

.. code-block:: python

   import praw

   reddit = praw.Reddit(user_agent='LMGTFY (by /u/USERNAME)',
                        client_id='CLIENT_ID', client_secret="CLIENT_SECRET",
                        username='USERNAME', password='PASSWORD')

If you're only analyzing public comments, enterring a username and password is optional.

Finding a comment source
~~~~~~~~~~~~~~~~~~~~~~~~

There are 2 main ways that you can extract comments with PRAW.

The first is to pick a subreddit, and then gather the ids or urls of threads in that subreddit however you'd like (e.g. by hot, new, top, etc.).

For example:

.. code-block:: python

   ids=[]
   subreddit = reddit.subreddit('Python').hot()
   for thread in subreddit:
       ids.append(thread.id)

The second option is to extract comments from a subreddit stream. This gives you a continuous stream (it'll keep going if you let it) of new comments to an entire subreddit.

Here's how that looks:

.. code-block:: python

   subreddit = reddit.subreddit('Python')
   for submission in subreddit.stream.submissions():
       #do something
       print(submission.body)

The ``body`` attribute of a :class:`.Submission` is a string of each each comment. You can do whatever you'd like with it at this point - you're done!

If you went with option 1, we still have a bit more work to do, so read on.

Extracting comments with PRAW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With a list of thread ids or urls at this point, you can now extract comments of specific threads.

Start by creating a new submission object, passing in either the ``id``
variable, or the ``url`` variable. Then, call the access the
:meth:`praw.models.reddit.subreddit.SubredditStream.comments` attribute.

.. code-block:: python

	submission = r.submission(id='IDNUMBER')
	comments = submission.comments

The comments object is now a :class:`.CommentForest` object, which contains all the top level comments of that thread.

Obviously, you'll probably want more than just the top-level comments. To get the children of those comments as well, use the 'list' method, as so:

.. code-block:: python

	comments_list=comments.list()

Now, you will have a list of comment objects. You can use dir(comments_list[0]) to see what you can do with them, but for the most part, you'll just want to get the string of each comment.

Here's how:

.. code-block:: python

	for comment in comments_list:
		print(comment.body)

There's one last problem to deal with. If you follow everything up until now, you'll see that some threads have comments that look like:

	<MoreComments count=10, children=[]>

:class:`.MoreComments` objects are comment trees that have not been expanded (just like when browsing the site normally). They usually don't have as many upvotes as the rest of the comments in a thread.

You can choose to take this into account and ignore them, or you can extract the comments from each of these :class:`.MoreComments` objects.

Just be warned, each time that you expand a :class:`.MoreComments` object, it will require an extra request to be made.

Here's how you do it:

.. code-block:: python

	comments.replace_more()
	comments_list=comments.list()

Calling the :meth:`.replace_more` method will replace the
:class:`.MoreComments` objects. Finally, you have the option to pass in 2
variables to the :meth:`.replace_more` method.

1. 'limit' - The maximum number of MoreComments instances to
   replace. Default is 32.

2. 'threshold' - The minimum number of children comments a
   MoreComments instance must have in order to be replaced.

Finally, note that if you go to a thread in your browser, the number of comments displayed may not match up 100% with the number of comments you extract here. They'll be close, but the count on the actual Reddit thread will also include deleted comments.
