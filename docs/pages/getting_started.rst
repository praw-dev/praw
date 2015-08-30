.. _getting_started:

Getting Started
===============

In this tutorial we'll go over everything needed to create a bot or program
using reddit's API through the Python Reddit API Wrapper (PRAW). We're going to
write a program that breaks down a redditor's karma by subreddit, just like the
reddit feature. Unlike that, our program can break it down for any redditor,
not just us. However, it will be less precise due to limitations in the reddit
API, but we're getting ahead of ourselves.

This is a beginners tutorial to PRAW. We'll go over the hows and whys of
everything from getting started to writing your first program accessing reddit.
What we won't go over in this tutorial is the Python code.

Connecting to reddit
--------------------

Start by firing up Python and importing PRAW. You can find the installation
instructions on the :ref:`main page <main_page>`.

.. code-block:: pycon

    >>> import praw

Next we need to connect to reddit and identify our script. We do this through
the ``user_agent`` we supply when our script first connects to reddit.

.. code-block:: pycon

    >>> user_agent = "Karma breakdown 1.0 by /u/_Daimon_"
    >>> r = praw.Reddit(user_agent=user_agent)

Care should be taken when we decide on what user_agent to send to reddit. The
``user_agent`` field is how we uniquely identify our script. The `reddit API
wiki page <https://github.com/reddit/reddit/wiki/API>`_ has the official and
updated recommendations on user_agent strings and everything else. Reading it
is *highly recommended*.

In addition to reddit's recommendations, your user_agent string should not
contain the keyword ``bot``.

Breaking Down Redditor Karma by Subreddit
-----------------------------------------

Now that we've established contact with reddit, it's time for the next step in
our script: to break down a user's karma by subreddit. There isn't a function
that does this, but luckily it's fairly easy to write the python code to do
this ourselves.

We use the function :meth:`.get_redditor` to get a :class:`.Redditor` instance
that represents a user on reddit. In the following case ``user`` will provide
access to the reddit user "\`\_Daimon\_\`".

.. code-block:: pycon

    >>> user_name = "_Daimon_"
    >>> user = r.get_redditor(user_name)

Next we can use the functions :meth:`~.Redditor.get_comments` and
:meth:`.get_submitted` to get that redditor's comments and submissions. Both
are a part of the superclass ``Thing`` as mentioned on the `reddit API wiki
page <https://github.com/reddit/reddit/wiki/API>`_. Both functions can be
called with the parameter ``limit``, which limits how many things we receive.
As a default, reddit returns 25 items. When the limit is set to ``None``, PRAW
will try to retrieve all the things. However, due to limitations in the reddit
API (not PRAW) we might not get all the things, but more about that later.
During development you should be nice and set the limit lower to reduce
reddit's workload, if you don't actually need all the results.

.. code-block:: pycon

    >>> thing_limit = 10
    >>> gen = user.get_submitted(limit=thing_limit)

Next we take the generator containing things (either comments or submissions)
and iterate through them to create a dictionary with the subreddit display
names (like *python* or *askreddit*) as keys and the karma obtained in those
subreddits as values.

>>> karma_by_subreddit = {}
>>> for thing in gen:
...     subreddit = thing.subreddit.display_name
...     karma_by_subreddit[subreddit] = (karma_by_subreddit.get(subreddit, 0)
...                                     + thing.score)

Finally, let's output the karma breakdown in a pretty format.

>>> import pprint
>>> pprint.pprint(karma_by_subreddit)

And we're done. The program could use a better way of displaying the data,
exception catching, etc. If you're interested, you can check out a more
fleshed out version of this `Karma-Breakdown
<https://github.com/Damgaard/Reddit-Bots/blob/master/karma_breakdown.py>`_
program.

Obfuscation and API limitations
-------------------------------

As I mentioned before there are limits in reddit's API. There is a limit to the
amount of things reddit will return before it barfs. Any single reddit listing
will display at most 1000 items. This is true for all listings including
subreddit submission listings, user submission listings, and user comment
listings.

You may also have realized that the karma values change from run to run. This
inconsistency is due to `reddit's obfuscation
<https://www.reddit.com/wiki/faq#wiki_how_is_a_submission.27s_score_determined.3F>`_
of the upvotes and downvotes. The obfuscation is done to everything and
everybody to thwart potential cheaters. There's nothing we can do to prevent
this.

Another thing you may have noticed is that retrieving a lot of elements take
time. reddit allows requests of up to 100 items at once. So if you request <=
100 items PRAW can serve your request in a single API call, but for larger
requests PRAW will break it into multiple API calls of 100 items each separated
by a small 2 second delay to follow the `api guidelines
<https://github.com/reddit/reddit/wiki/API>`_. So requesting 250 items will
require 3 api calls and take at least 2x2=4 seconds due to API delay. PRAW does
the API calls lazily, i.e. it will not send the next api call until you
actually need the data. Meaning the runtime is max(api_delay, code execution
time).

Continue to the next tutorial. :ref:`writing_a_bot`.

The full Karma Breakdown program.
---------------------------------

.. code-block:: python

    import praw

    user_agent = ("Karma breakdown 1.0 by /u/_Daimon_ "
                  "github.com/Damgaard/Reddit-Bots/")
    r = praw.Reddit(user_agent=user_agent)
    thing_limit = 10
    user_name = "_Daimon_"
    user = r.get_redditor(user_name)
    gen = user.get_submitted(limit=thing_limit)
    karma_by_subreddit = {}
    for thing in gen:
        subreddit = thing.subreddit.display_name
        karma_by_subreddit[subreddit] = (karma_by_subreddit.get(subreddit, 0)
                                         + thing.score)
    import pprint
    pprint.pprint(karma_by_subreddit)
