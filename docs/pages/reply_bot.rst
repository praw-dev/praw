Submission Stream Reply Bot
===========================

Most redditors have seen bots in action on the site. Reddit bots can perform a
number of tasks including providing useful information, e.g., an Imperial to
Metric units bot; convenience, e.g., a link corrector bot; or analytical
information, e.g., redditor analyzer bot for writing complexity.

PRAW provides a simple way to build your own bot using the python programming
language. As a result, it is little surprise that a majority of bots on Reddit
are powered by PRAW.

This tutorial will show you how to build a bot that monitors a particular
subreddit, `/r/AskReddit <https://www.reddit.com/r/AskReddit/>`_, for new
submissions containing simple questions and replies with an appropriate link to
`lmgtfy <http://lmgtfy.com/>`_ (Let Me Google This For You).

There are three key components we will address to perform this task:

1. Monitor new submissions.

2. Analyze the title of each submission to see if it contains a simple
   question.

3. Reply with an appropriate lmgtfy link.

LMGTFY Bot
----------

The goal of the LMGTFY Bot is to point users in the right direction when they
ask a simple question that is unlikely to be upvoted or answered by other
users.

Two examples of such questions are:

1. "What is the capital of Canada?"

2. "How many feet are in a yard?"

Once we identify these questions, the LMGTFY Bot will reply to the submission
with an appropriate `lmgtfy <http://lmgtfy.com/>`_ link. For the example
questions those links are:

1. http://lmgtfy.com/?q=What+is+the+capital+of+Canada%3F

2. http://lmgtfy.com/?q=How+many+feet+are+in+a+yard%3F


Step 1: Getting Started
~~~~~~~~~~~~~~~~~~~~~~~

Access to Reddit's API requires a set of OAuth2 credentials. Those credentials
are obtained by registering an application with Reddit. To register an
application and receive a set of OAuth2 credentials lease follow only the
"First Steps" section of Reddit's `OAuth2 Quick Start Example
<https://github.com/reddit/reddit/wiki/OAuth2-Quick-Start-Example#first-steps>`_
wiki page.

Once the credentials are obtained we can begin writing the LMGTFY bot. Start by
creating an instance of :class:`.Reddit`:

.. code-block:: python

   import praw

   reddit = praw.Reddit(user_agent='LMGTFY (by /u/USERNAME)',
                        client_id='CLIENT_ID', client_secret="CLIENT_SECRET",
                        username='USERNAME', password='PASSWORD')

In addition to the OAuth2 credentials, the username and password of the Reddit
account that registered the application are required.

.. note:: This example demonstrates use of a *script* type application. For
   other application types please see Reddit's wiki page `OAuth2 App Types
   <https://github.com/reddit/reddit/wiki/oauth2-app-types>`_.


Step 2: Monitoring New Submissions to /r/AskReddit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PRAW provides a convenient way to obtain new submissions to a given
subreddit. To indefinitely iterate over new submissions to a subreddit add:

.. code-block:: python

   subreddit = reddit.subreddit('AskReddit')
   for submission in subreddit.stream.submissions():
       # do something with submission

Replace `AskReddit` with the name of another subreddit if you want to iterate
through its new submissions. Additionally multiple subreddits can be specified
by joining them with pluses, for example ``AskReddit+NoStupidQuestions`, and
all subreddits can be specified using the special name ``all``.

Step 3: Analyzing the Submission Titles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that we have a stream of new submissions to /r/AskReddit, it is time to see
if their title's contain a simple question. We naïvely definte a simple
question as:

1. It must contain no more than ten words.

2. It must contain one of the phrases "what is", "what are", or "who is".

.. warning:: These naïve criteria result in many false positives. It is
   strongly recommended that you develop more precise heuristics before
   launching a bot on any popular subreddits.

First we filter out titles that contain more than ten words:

.. code-block:: python

   if len(submission.title.split()) > 10:
           return

Then we check to see if the submission's title contains any of the desired
phrases:

.. code-block:: python

   questions = ['what is', 'who is', 'what are']
   normalized_title = submission.title.lower()
   for question_phrase in questions:
       if question_phrase in normalized_title:
           # do something with a matched submission
           break

String comparision in python is case sensitive. As a result, we only compare a
normalized version of the title to our lower-case question phrases. In this
case, "noralized" means only lower-case.

The ``break`` at the end prevents us from matching more than once on a single
submission. For instance, what would happen without the ``break`` if a
submission's title was "Who is or what are buffalo?"

Step 4: Automatically Replying to the Submission
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We're almost there, the last part is to make a reply request to the Reddit
API. Thankfully, it's really simple with PRAW.

But first, we'll need to figure out what link to send people to in our
comments.

By analyzing the lmgtfy links from earlier, the main things we need to do is
change spaces to "+", and question marks to "%3F"
(http://lmgtfy.com/?q=What+is+the+capital+of+Canada%3F).

Here's a very simple function to do so:

.. code-block:: python

   def fixurl(phrase):
       removespaces = phrase.replace(" ", "+")
       removequestions = removespaces.replace("?", "%3F")
       return removequestions

Then, we can format the text that we want to include in our reply (according to
Reddit formatting guidelines), and make the reply:

.. code-block:: python

   for id_number in ids:
       submission = reddit.submission(id=id_number)
       title = submission.title.lower()
       for question_type in questions:
           if question_type in title:
               # make the reply
               correct_url = fixurl(title)
               reply_text="[Here's a link that might help](http://lmgtfy.com/?q=%s)" % (correct_url)
               # send the actual reply request
               submission.reply(reply_text)

If all went well, your post should have been made. Keep in mind that if your
bot account is brand new, you'll be limited in how many posts you can make
until you build up some karma. You may also have to manually answer Captchas at
the start.

Step 5: Tying it all together
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The main thing that we're missing is a way to run the bot continuously, and to
not do the same work twice.

In order to do that, we'll place all the main code inside a 'while' loop.

As for the second part, when your 'subreddit' object returns the information
about the AskReddit submissions, they are returned in order, just like you
would see if you visited /r/AskReddit/new yourself.

So in order to prevent our bot from checking the same submissions twice, we
only need to record the most recent submission ID, and check it when the while
loop is executed next.

.. code-block:: python

   while True:
       ids=[]
       if ids:
           latest_id=ids[0]
       else:
           latest_id=''

This checks to make sure that the code has been run before ("if ids"), and then
assigns the most recent submission ID (newest submitted) to the variable
"latest_id".

Finally, one more loop before the main code is executed will prevent any
duplicate work:

.. code-block:: python

    # remove any already examined submissions
    if latest_id in ids:
        position = ids.index(latest_id)
        ids=ids[0:position]

This checks to see if we've already checked any submissions in our newly
created list of ids before, and cleaves off those old submissions if we have.

The Complete LMGTFY Bot
~~~~~~~~~~~~~~~~~~~~~~~

.. include:: ../examples/lmgtfy_bot.py
   :code: python
