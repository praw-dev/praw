A Simple Stream-Based Reply Bot
===============================

Any Redditor has seen bots in action on the site. They can provide useful
information (like an Imperial to Metric bot), convenience (link corrector
bots), or analytical information (redditor analyzer bot for writing
complexity), among other things.

PRAW is the simplest way to build your own bot using Python.

This tutorial will show you how to build a bot that monitors a particular
subreddit (/r/AskReddit), and replies to new threads that contain simple
questions with a link to "lmgtfy.com" (Let Me Google This For You).

To do this, there are 3 key components we'll have to address:

1. A way to monitor new threads.

2. A way to analyze the titles of those threads and see if they contain a
   simple question.

3. A way make the desired reply.

Working demo: LMGTFY Bot
------------------------

Our goal is to point users in the right direction when they ask a simple
question that is unlikely to be upvoted or answered by other users.

I'm referring to simple questions like:

1. "What is the capital of Canada?"

2. "How many feet are in a yard?"

we identify these questions, our bot will send a link to lmgtfy.com with the
query attached to it. For those above questions, the links would look like
this:

1. http://lmgtfy.com/?q=What+is+the+capital+of+Canada%3F

2. http://lmgtfy.com/?q=How+many+feet+are+in+a+yard%3F

Let's start by setting up a basic PRAW instance:

.. code-block:: python

   import praw

   r = praw.Reddit(user_agent='Let me Google that for you Bot',
                   client_id='CLIENT_ID', client_secret="CLIENT_SCRET",
                   username='USERNAME', password='PASSWORD')

As usual, you will need an Oauth client_id and client_secret key for your bot
(See Oauth set-up instructions here).

Additionally, you'll need to supply the credentials of your bot's account in
the form of the "username" and "password" variables passed to the main Reddit
instance.

Step 1: Monitor New Threads and Grab the titles
-----------------------------------------------

To get the threads (submissions) to a subreddit, we simply need to call the
subreddit method of our "r" object, like so:

.. code-block:: python

   subreddit= r.subreddit('askreddit').new(limit=100)

The limit here is 100 by default (so you could remove it), but you could change
it if desired.

This code creates a lazy-loaded subreddit object.

Next, we'll need to extract the thread ids for each submission in the
subreddit.

Here's how:

.. code-block:: python

    ids=[]
    for thread in subreddit:
        ids.append(thread.id)

Once we have the ids, we can create a submission object for each thread, and
extract/store the titles.

.. code-block:: python

    for id_number in ids:
        thread = r.submission(id=id_number)
        title = thread.title.lower()

Step 2: Analyze the Titles
--------------------------

Now that we have the titles of the threads in the "new" feed of /r/AskReddit,
it's time to see if they contain a simple question in them.

This might mean that they contain strings like:

* "what is"
* "who is"
* "what are"

And so on...You could get a lot for complicated, even considering title
length. However, for the sake of this example, these 3 phrases will be enough.

Create an array that contains these strings.

.. code-block:: python

   questions  = ['what is', 'who is', 'what are']

Then, let's revisit our for-loop from above and check to see if the titles
contain any of these:

.. code-block:: python

   for id_number in ids:
       thread = r.submission(id=id_number)
       title = thread.title.lower()
       for question_type in questions:
           if question_type in title:
               #make the reply

Step 3: Make an Automated Reply
-------------------------------

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
       thread = r.submission(id=id_number)
       title = thread.title.lower()
       for question_type in questions:
           if question_type in title:
               # make the reply
               correct_url = fixurl(title)
               reply_text="[Here's a link that might help](http://lmgtfy.com/?q=%s)" % (correct_url)
               # send the actual reply request
               thread.reply(reply_text)

If all went well, your post should have been made. Keep in mind that if your
bot account is brand new, you'll be limited in how many posts you can make
until you build up some karma. You may also have to manually answer Captchas at
the start.

Loose ends for continuous running
---------------------------------

Time to tie it altogther.

The main thing that we're missing is a way to run the bot continuously, and to
not do the same work twice.

In order to do that, we'll place all the main code inside a 'while' loop.

As for the second part, when your 'subreddit' object returns the information
about the AskReddit threads, they are returned in order, just like you would
see if you visited /r/AskReddit/new yourself.

So in order to prevent our bot from checking the same threads twice, we only
need to record the most recent thread ID, and check it when the while loop is
executed next.

.. code-block:: python

   while True:
       ids=[]
       if ids:
           latest_id=ids[0]
       else:
           latest_id=''

This checks to make sure that the code has been run before ("if ids"), and then
assigns the most recent thread ID (newest submitted) to the variable
"latest_id".

Finally, one more loop before the main code is executed will prevent any
duplicate work:

.. code-block:: python

    # remove any already examined threads
    if latest_id in ids:
        position = ids.index(latest_id)
        ids=ids[0:position]

This checks to see if we've already checked any threads in our newly created
list of ids before, and cleaves off those old threads if we have.

Completed Code
--------------

The final code will show you how all these pieces fit together.

.. code-block:: python

   import time

   import praw

   r = praw.Reddit(user_agent='Let me Google that for you Bot',
                   client_id='CLIENT_ID', client_secret="CLIENT_SCRET",
                   username='USERNAME', password='PASSWORD')

   questions = ['what is', 'who is', 'what are']


   def fixurl(phrase):
       removespaces = phrase.replace(" ", "+")
       removequestions = removespaces.replace("?", "%3F")
       return removequestions


   while True:
       ids = []

       # Check if we've already done some of the work
       if ids:
           latest_id = ids[0]
       else:
           latest_id = ''

       subreddit = r.subreddit('askreddit').new(limit=6)

       for x in subreddit:
           ids.append(x.id)

       # Remove any already examined threads
       if latest_id in ids:
           position = ids.index(latest_id)
           ids = ids[0:position]

       # Identify title strings that match conditions
       for id_number in ids:
           thread = r.submission(id=id_number)
           title = thread.title.lower()
           for question_type in questions:
               if question_type in title:
                   # make the reply
                   correct_url = fixurl(title)
                   reply_text = "[Here's a link that might help]\(http://lmgtfy.com/?q=%s)" % (correct_url)
                   # send the actual reply request
                   thread.reply(reply_text)
