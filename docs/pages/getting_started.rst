.. _getting_started:

Getting Started
===============

In this turorial we'll go over everything needed to create a bot or program
using reddit's API through the Python Reddit API Wrapper (PRAW). We're going to
write a program that breaks down a redditor's karma by subreddit, just like the
`reddit gold <http://www.reddit.com/help/gold>`_ feature. Unlike that, our
program can break it down for any redditor, not just us. However, it will be
less precise due to limitations in the reddit API, but we're getting ahead of
ourselves.

This is a beginners tutorial to PRAW. We'll go over the hows and whys of
everything from getting started to writing your first program accessing reddit.
What we won't go over in this tutorial is the Python code.

Connecting to Reddit
--------------------

Start by firing up Python and importing PRAW. You can find the module and
installation instructions in the `python module description
<https://github.com/praw-dev/praw>`_.

.. code-block:: pycon

    >>> import praw

Next we need to connect to reddit and identify our script. We do this through
the ``user_agent`` we supply when our script first connects to reddit.

.. code-block:: pycon

    >>> user_agent = ("Karma breakdown 1.0 by /u/_Daimon_ "
    ...               "github.com/Damgaard/Reddit-Bots/")
    >>> r = praw.Reddit(user_agent=user_agent)

Care should be taken when we decide on what user_agent to send to reddit. The
``user_agent`` field is how we uniquely identify our script. The `reddit API
wiki page <https://github.com/reddit/reddit/wiki/API>`_ has the official and
updated recommendations on user_agent strings and everything else. Reading it
is *highly recommended*. Here's the part about user_agent recommendations
included for the sake of completion.

----

* Change your client's User-Agent string to something unique and descriptive,
  preferably referencing your reddit username.

    * Example: ``User-Agent: super happy flair bot v1.0 by /u/spladug``
    * Many default User-Agents (like "Python/urllib" or "Java") are drastically
      limited to encourage unique and descriptive user-agent strings.
    * If you're making an application for others to use, please include a
      version number in the user agent. This allows us to block buggy versions
      without blocking all versions of your app.
    * **NEVER lie about your user-agent.** This includes spoofing popular
      browsers and spoofing other bots. We will ban liars with extreme
      prejudice.

----

In addition to reddit's recommendations, it's nice to to add a link to the
script's source (if available).

Breaking down Redditor Karma by Subreddit
-----------------------------------------

Now that we've established contact with reddit, it's time for the next step in
our script to break down a user's karma by subreddit. There isn't a function
that does this, but luckily it's fairly easy to write the python code to do
this ourselves.

We use the function ``get_redditor`` to get a ``Redditor`` instance that
represents a user on reddit. In the following case ``user`` will provide access
to the reddit user "\`\_Daimon\_\`".

.. code-block:: pycon

    >>> user_name = "_Daimon_"
    >>> user = r.get_redditor(user_name)

Next we can use the functions ``get_comments`` and ``get_submitted`` to get
that redditor's comments and submissions. Both are a part of the superclass
``Thing`` as mentioned on the `reddit API wiki page
<https://github.com/reddit/reddit/wiki/API>`_. Both functions can be called
with the parameter ``limit``, which limits how many things we receive. As a
default, PRAW makes calls to reddit with ``limit=25``. The default can be
edited in the module's configuration files. When the limit is set to ``None``,
PRAW will try to retrieve all the things. However, due to limitations in the
reddit API (not PRAW) we might not get all the things, but more about that
later. During development you should be nice and set the limit lower to reduce
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

And we're done. The program could use a way of displaying the data, exception
catching, etc. If you're interested, you can check out a more fleshed out
version of this `Karma-Breakdown
<https://github.com/Damgaard/Reddit-Bots/blob/master/karma_breakdown.py>`_
program.

Obfuscation and API limitations
-------------------------------

As I mentioned before there are limits in reddit's API. There is a limit to the
amount of things reddit will return before it barfs. Any single reddit listing
will display at most 1000 items. This is true for all listings including
subreddit submission listings, user submission listings, and user comment
listings.

You may also have realised that the karma values change from run to run. This
inconsistency is due to `reddit's obfuscation <http://ww.reddit.com/help/faqs/
help#Whydothenumberofvoteschangewhenyoureloadapage>`_ of the upvotes and
downvotes. The obfuscation is done to everything and everybody to thwart
potential cheaters. There's nothing we can do to prevent this.

Another thing you will probably have noticed is that retrieving a lot of
elements take a lot of time. Our requests are broken into pieces of 25 things
by PRAW, and then sent sequentially to reddit. But they are separated by a
delay of 2 seconds, to follow the guidelines in the `reddit API wiki page
<https://github.com/reddit/reddit/wiki/API>`_. Therefore retrieving 100 things,
will cost 2x4=8 seconds to API delay.

Continue to the next tutorial. :ref:`writing_a_bot`.
