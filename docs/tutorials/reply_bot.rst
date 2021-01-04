Submission Stream Reply Bot
===========================

Most redditors have seen bots in action on the site. Reddit bots can perform a number of
tasks including providing useful information, e.g., an Imperial to Metric units bot;
convenience, e.g., a link corrector bot; or analytical information, e.g., redditor
analyzer bot for writing complexity.

PRAW provides a simple way to build your own bot using the python programming language.
As a result, it is little surprise that a majority of bots on Reddit are powered by
PRAW.

This tutorial will show you how to build a bot that monitors a particular subreddit,
`r/AskReddit <https://www.reddit.com/r/AskReddit/>`_, for new submissions containing
simple questions and replies with an appropriate link to lmgtfy_ (Let Me Google That For
You).

There are three key components we will address to perform this task:

1. Monitor new submissions.

2. Analyze the title of each submission to see if it contains a simple question.

3. Reply with an appropriate lmgtfy_ link.

LMGTFY Bot
----------

The goal of the LMGTFY Bot is to point users in the right direction when they ask a
simple question that is unlikely to be upvoted or answered by other users.

Two examples of such questions are:

1. "What is the capital of Canada?"

2. "How many feet are in a yard?"

Once we identify these questions, the LMGTFY Bot will reply to the submission with an
appropriate lmgtfy_ link. For the example questions those links are:

1. https://lmgtfy.com/?q=What+is+the+capital+of+Canada%3F

2. https://lmgtfy.com/?q=How+many+feet+are+in+a+yard%3F


Step 1: Getting Started
~~~~~~~~~~~~~~~~~~~~~~~

Access to Reddit's API requires a set of OAuth2 credentials. Those credentials are
obtained by registering an application with Reddit. To register an application and
receive a set of OAuth2 credentials please follow only the "First Steps" section of
Reddit's `OAuth2 Quick Start Example`_ wiki page.

Once the credentials are obtained we can begin writing the LMGTFY Bot. Start by creating
an instance of :class:`.Reddit`:

.. code-block:: python

    import praw

    reddit = praw.Reddit(
        user_agent="LMGTFY (by u/USERNAME)",
        client_id="CLIENT_ID",
        client_secret="CLIENT_SECRET",
        username="USERNAME",
        password="PASSWORD"
    )

In addition to the OAuth2 credentials, the username and password of the Reddit account
that registered the application are required.

.. note::

    This example demonstrates use of a *script* type application. For other application
    types please see Reddit's wiki page `OAuth2 App Types
    <https://github.com/reddit/reddit/wiki/oauth2-app-types>`_.


Step 2: Monitoring New Submissions to r/AskReddit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PRAW provides a convenient way to obtain new submissions to a given subreddit. To
indefinitely iterate over new submissions to a subreddit add:

.. code-block:: python

    subreddit = reddit.subreddit("AskReddit")
    for submission in subreddit.stream.submissions():
        # do something with submission
        ...

Replace ``AskReddit`` with the name of another subreddit if you want to iterate through
its new submissions. Additionally multiple subreddits can be specified by joining them
with pluses, for example ``AskReddit+NoStupidQuestions``. All subreddits can be
specified using the special name ``all``.

Step 3: Analyzing the Submission Titles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that we have a stream of new submissions to r/AskReddit, it is time to see if their
titles contain a simple question. We naïvely define a simple question as:

1. It must contain no more than ten words.

2. It must contain one of the phrases "what is", "what are", or "who is".

.. warning::

    These naïve criteria result in many false positives. It is strongly recommended that
    you develop more precise heuristics before launching a bot on any popular
    subreddits.

First we filter out titles that contain more than ten words:

.. code-block:: python

   if len(submission.title.split()) > 10:
       return

We then check to see if the submission's title contains any of the desired phrases:

.. code-block:: python

    questions = ["what is", "who is", "what are"]
    normalized_title = submission.title.lower()
    for question_phrase in questions:
        if question_phrase in normalized_title:
            # do something with a matched submission
            break

String comparison in Python is case sensitive. As a result, we only compare a normalized
version of the title to our lower-case question phrases. In this case, "normalized"
means only lower-case.

The ``break`` at the end prevents us from matching more than once on a single
submission. For instance, what would happen without the ``break`` if a submission's
title was "Who is or what are buffalo?"

Step 4: Automatically Replying to the Submission
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The LMGTFY Bot is nearly complete. We iterate through submissions, and find ones that
appear to be simple questions. All that is remaining is to reply to those submissions
with an appropriate lmgtfy_ link.

First we will need to construct a working lmgtfy_ link. In essence we want to pass the
entire submission title to lmgtfy_. However, there are certain characters that are not
permitted in URLs or have other meanings. For instance, the space character, " ", is not
permitted, and the question mark, "?", has a special meaning. Thus we will transform
those into their URL-safe representation so that a question like "What is the capital of
Canada?" is transformed into the link
``https://lmgtfy.com/?q=What+is+the+capital+of+Canada%3F``.

There are a number of ways we could accomplish this task. For starters we could write a
function to replace spaces with pluses, ``+``, and question marks with ``%3F``. However,
there is even an easier way; using an existing built-in function to do so.

Add the following code where the "do something with a matched submission" comment is
located:

.. code-block:: python

    from urllib.parse import quote_plus

    reply_template = '[Let me google that for you](https://lmgtfy.com/?q={})'

    url_title = quote_plus(submission.title)
    reply_text = reply_template.format(url_title)

Now that we have the reply text, replying to the submission is easy:

.. code-block:: python

    submission.reply(reply_text)

If all went well, your comment should have been made. If your bot account is brand new,
you will likely run into rate limit issues. These rate limits will persist until that
account acquires sufficient karma.

Step 5: Cleaning Up The Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While we have a working bot, we have added little segments here and there. If we were to
continue to do so in this fashion our code would be quite unreadable. Let's clean it up
some.

The first thing we should do is put all of our import statements at the top of the file.
It is common to list built-in packages before third party ones:

.. include:: ../examples/lmgtfy_bot.py
   :code: python
   :end-line: 3

Next we extract a few constants that are used in our script:

.. include:: ../examples/lmgtfy_bot.py
   :code: python
   :start-line: 4
   :end-line: 6

We then extract the segment of code pertaining to processing a single submission into
its own function:

.. include:: ../examples/lmgtfy_bot.py
   :code: python
   :start-line: 18
   :end-line: 33

Observe that we added some comments and a ``print`` call. The ``print`` addition informs
us every time we are about to reply to a submission, which is useful to ensure the
script is running.

Next, it is a good practice to not have any top-level executable code in case you want
to turn your Python script into a Python module, i.e., import it from another Python
script or module. A common way to do that is to move the top-level code to a ``main``
function:

.. include:: ../examples/lmgtfy_bot.py
   :code: python
   :start-line: 8
   :end-line: 16

Finally we need to call ``main`` only in the cases that this script is the one being
executed:

.. include:: ../examples/lmgtfy_bot.py
   :code: python
   :start-line: 35

The Complete LMGTFY Bot
~~~~~~~~~~~~~~~~~~~~~~~

The following is the complete LMGTFY Bot:

.. literalinclude:: ../examples/lmgtfy_bot.py
   :language: python


.. _lmgtfy: https://lmgtfy.com/
.. _OAuth2 Quick Start Example:
   https://github.com/reddit/reddit/wiki/OAuth2-Quick-Start-Example#first-steps
