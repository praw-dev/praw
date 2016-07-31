.. _overview:

Code Overview
=============

Here you will find an overview of PRAW's objects and methods, but not the
objects attributes which are generated dynamically from reddit's responses and
are thus impossible to accurately describe statically.

Top Level Classes
-----------------

.. autoclass:: praw.Reddit
   :inherited-members:

Models
------

.. automodule:: praw.models
   :inherited-members:

Submission Utility Classes
--------------------------

.. autoclass:: praw.models.comment_forest.CommentForest
   :inherited-members:

.. autoclass:: praw.models.reddit.submission.SubmissionFlair
   :inherited-members:

.. autoclass:: praw.models.reddit.submission.SubmissionModeration
   :inherited-members:

Subreddit Utility Classes
-------------------------

.. autoclass:: praw.models.reddit.subreddit.SubredditFlair
   :inherited-members:

.. autoclass:: praw.models.reddit.subreddit.SubredditModeration
   :inherited-members:

.. autoclass:: praw.models.reddit.subreddit.SubredditRelationship
   :inherited-members:

.. autoclass:: praw.models.reddit.subreddit.SubredditStream
   :inherited-members:

.. autoclass:: praw.models.reddit.subreddit.SubredditWiki
   :inherited-members:

Other Classes
-------------

.. autoclass:: praw.config.Config
   :inherited-members:

.. autoclass:: praw.objector.Objector
   :inherited-members:

.. autoclass:: praw.models.reddit.wikipage.WikiPageModeration
   :inherited-members:

Exceptions
----------

.. autoexception:: praw.exceptions.PRAWException

.. autoexception:: praw.exceptions.APIException

.. autoexception:: praw.exceptions.ClientException
