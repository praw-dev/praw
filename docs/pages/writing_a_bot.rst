.. _writing_a_bot:

Writing a reddit Bot
====================

In the :ref:`getting_started` tutorial, we wrote a script to break down a
redditor's karma. In this tutorial we will write a bot.

Bots differ from scripts in a few different ways. First, bots normally run
continuously whereas scripts are most often one-off jobs. Second, bots
usually automate some task that could be performed by a user, such as posting,
commenting or moderating. Bots also present unique design challenges not
applicable to writing scripts. We need to make sure that bots keep working
continuously, don't unnecessarily perform the same task twice and keep within
`API Guidelines <https://github.com/reddit/reddit/wiki/API>`_. This tutorial
will introduce you to all three of these problems and show how to use PRAW's
and reddit's documentation.

The Problem
-----------

From time to time questions are submitted to reddit.com about PRAW, mellort's
deprecated fork and the reddit API in general. `\u\_Daimon_` wants to be
notified of these submissions, so he can help the submitter. The bot will
monitor the subreddits `r/python <http://www.reddit.com/r/python>`_,
`r/learnpython`_ and `r/redditdev <http://www.reddit.com/r/redditdev>`_ and
send `\u\_Daimon_` a private message, whenever it detects a post with such a
question.

We start by importing PRAW and logging in.

>>> import time
>>> import praw
>>> r = praw.Reddit('PRAW related-question monitor by /u/_Daimon_ v 1.0. '
...                 'Url: https://praw.readthedocs.org/en/latest/'
...                 'pages/writing_a_bot.html')
>>> r.login()
>>> already_done = [] # Ignore this for now

The next step is the main loop, where we look at each of the subreddits in
turn. For this tutorial we will implement a subset of the bot, which only looks
at the submissions in `r/learnpython`_ to make the example code as clear as
possible.

>>> while True:
>>> subreddit = r.get_subreddit('learnpython')
>>> for submission in subreddit.get_hot(limit=10):
        # Test if it contains a PRAW-related question

Finding what we need
^^^^^^^^^^^^^^^^^^^^

Now that we have the submissions, we need to see if they contain a PRAW-related
question. We are going to look at the text part of a submission to see if it
contains one of the strings "reddit api", "praw" or "mellort". So we're going
to go through how you can find out stuff like this on your own.

Start the Python interpreter and compare the output with `this r/learnpython
<http://www.reddit.com/r/learnpython/comments/105aru/newbie_stripping_strings_
of_last_character/>`_ post.

.. code-block:: pycon

    >>> import praw
    >>> from pprint import pprint
    >>> r = praw.Reddit('Submission variables testing by /u/_Daimon_')
    >>> submission = r.get_submission(submission_id = "105aru")
    >>> pprint(vars(submission))
    {'_comment_sort': None,
    '_comments': [<praw.objects.Comment object at 0x030FF330>,
                <praw.objects.Comment object at 0x03107B70>,
                <praw.objects.Comment object at 0x03107CF0>],

    '_comments_by_id': {u't1_c6aijmu': <praw.objects.Comment object at 0x030FF330>,
                        u't1_c6ailrj': <praw.objects.Comment object at 0x03107B70>,
                        u't1_c6ailxt': <praw.objects.Comment object at 0x03107CF0>,
                        u't1_c6ak4rq': <praw.objects.Comment object at 0x03107C50>,
                        u't1_c6akq4n': <praw.objects.Comment object at 0x03107BB0>,
                        u't1_c6akv1g': <praw.objects.Comment object at 0x031077D0>}
                        ,

    '_info_url': 'http://www.reddit.com/api/info/',
    '_orphaned': {},
    '_populated': True,
    '_replaced_more': False,
    '_underscore_names': None,
    'approved_by': None,
    'author': Redditor(user_name='Blackshirt12'),
    'author_flair_css_class': u'py32bg',
    'author_flair_text': u'',
    'banned_by': None,
    'clicked': False,
    'created': 1348081369.0,
    'created_utc': 1348077769.0,
    'domain': u'self.learnpython',
    'downs': 0,
    'edited': 1348083784.0,
    'hidden': False,
    'id': u'105aru',
    'is_self': True,
    'likes': None,
    'link_flair_css_class': None,
    'link_flair_text': None,
    'media': None,
    'media_embed': {},
    'name': u't3_105aru',
    'num_comments': 6,
    'num_reports': None,
    'over_18': False,
    'permalink': u'http://www.reddit.com/r/learnpython/comments/105aru/newbie_stri
    pping_strings_of_last_character/',
    'reddit_session': <praw.Reddit object at 0x029477F0>,
    'saved': False,
    'score': 1,
    'selftext': u'Update: Thanks for the help. Got fixed.\n\nI need to strip 3
    strin gs in a list of 4 of their trailing commas to get my formatting right
    and to conv ert one of them (a number) to a float but I\'m confused on the
    syntax. Also, I do n\'t know of an efficient way of completing the task; I was
    planning on stripping each of the three strings on a new line.\n\n    for line
    in gradefile:\n linelist = string.split(line)\n        #strip linelist[0],[1],
    and [2] of commas\ n        linelist = string.rstrip(linelist[0], ",")',
    'selftext_html': u'&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;Update:
    Thanks for the help. Got fixed.&lt;/p&gt;\n\n&lt;p&gt;I need to strip 3
    strings in a list of 4 of their trailing commas to get my formatting right and
    to convert o ne of them (a number) to a float but I&amp;#39;m confused on the
    syntax. Also, I don&amp;#39;t know of an efficient way of completing the task;
    I was planning on stripping each of the three strings on a new
    line.&lt;/p&gt;\n\n&lt;pre&gt;&lt;co de&gt;for line in gradefile:\n
    linelist = string.split(line)\n    #strip linel ist[0],[1], and [2] of
    commas\n    linelist = string.rstrip(linelist[0], &amp;quo
    t;,&amp;quot;)\n&lt;/code&gt;&lt;/pre&gt;\n&lt;/div&gt;&lt;!-- SC_ON --&gt;',
    'subreddit': <praw.objects.Subreddit object at 0x030FF030>,
    'subreddit_id': u't5_2r8ot',
    'thumbnail': u'',
    'title': u'Newbie: stripping strings of last character',
    'ups': 1,
    'url': u'http://www.reddit.com/r/learnpython/comments/105aru/newbie_stripping_
    strings_of_last_character/'}
    >>> pprint(dir(submission))
    ['__class__',
    '__delattr__',
    '__dict__',
    '__doc__',
    '__eq__',
    '__format__',
    '__getattr__',
    '__getattribute__',
    '__hash__',
    '__init__',
    '__module__',
    '__ne__',
    '__new__',
    '__reduce__',
    '__reduce_ex__',
    '__repr__',
    '__setattr__',
    '__sizeof__',
    '__str__',
    '__subclasshook__',
    '__unicode__',
    '__weakref__',
    '_comment_sort',
    '_comments',
    '_comments_by_id',
    '_extract_more_comments',
    '_get_json_dict',
    '_info_url',
    '_insert_comment',
    '_orphaned',
    '_populate',
    '_populated',
    '_replaced_more',
    '_underscore_names',
    '_update_comments',
    'add_comment',
    'approve',
    'approved_by',
    'author',
    'author_flair_css_class',
    'author_flair_text',
    'banned_by',
    'clear_vote',
    'clicked',
    'comments',
    'created',
    'created_utc',
    'delete',
    'distinguish',
    'domain',
    'downs',
    'downvote',
    'edit',
    'edited',
    'from_api_response',
    'from_id',
    'from_url',
    'fullname',
    'hidden',
    'hide',
    'id',
    'is_self',
    'likes',
    'link_flair_css_class',
    'link_flair_text',
    'mark_as_nsfw',
    'media',
    'media_embed',
    'name',
    'num_comments',
    'num_reports',
    'over_18',
    'permalink',
    'reddit_session',
    'refresh',
    'remove',
    'replace_more_comments',
    'report',
    'save',
    'saved',
    'score',
    'selftext',
    'selftext_html',
    'set_flair',
    'short_link',
    'subreddit',
    'subreddit_id',
    'thumbnail',
    'title',
    'undistinguish',
    'unhide',
    'unmark_as_nsfw',
    'unsave',
    'ups',
    'upvote',
    'url',
    'vote']

``vars`` contain the object's attributes and the values they contain. For
instance we can see that it has the variable ``title`` with the value
``u'Newbie: stripping strings of last character``. ``dir`` returns the names in
the local scope. You can also use ``help`` for introspection, if you wish to
generate a longer help page.  Worth noting is that PRAW contains a lot of
property-decorated functions, i.e., functions that are used as variables. So if
you're looking for something that behaves like a variable, it might not be in
vars. One of these is :attr:`.short_link`, which returns a much shorter url to
the submission and is called as a variable.

Another way of finding out how a reddit page is translated to variables is to
look at the .json version of that page. Just append .json to a reddit url to
look at the json version, such as the `previous r/learnpython post
<http://www.reddit.com/r/learnpython/comments/105aru/newbie_stripping_strings_
of_last_character/.json>`_. The variable name reddit uses for a variable is
almost certainly the same PRAW uses.

The 3 Bot Problems.
-------------------

Not Doing The Same Work Twice.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From the information we gained in the previous section, we see that the text
portion of a submission is stored in the variable ``selftext``. So we test if
any of the strings are within the ``selftext``, and if they are the bot sends
me a message. But `\u\_Daimon_` should only ever receive a single message per
submission.  So we need to maintain a list of the submissions we've already
notified `\u\_Daimon_` about.  Each ``Thing`` has a unique ID, so we simply
store the used ones in a list and check for membership before mailing. Finally
we sleep 30 minutes and restart the main loop.

>>> prawWords = ['praw', 'reddit_api', 'mellort']
>>> op_text = submission.selftext.lower()
>>> has_praw = any(string in op_text for string in prawWords)
>>> if submission.id not in already_done and has_praw:
...     msg = '[PRAW related thread](%s)' % submission.short_link
...     r.send_message('_Daimon_', 'PRAW Thread', msg)
...     already_done.append(submission.id)
>>> time.sleep(1800)

Note that if the authenticated account has less than 2 link karma then PRAW
will prompt for a captcha on stdin. Similar to how reddit would prompt for a
captcha if the authenticated user tried to send the message via the webend.

Running Continually.
^^^^^^^^^^^^^^^^^^^^

reddit.com is going to crash and other problems will occur. That's a fact of
life. Good bots should be able to take this into account and either exit
gracefully or survive the problem. This is a simple bot, where the loss of all
data isn't very problematic. So for now we're simply going to accept that it
will crash with total loss of data at the first problem encountered.

Keeping Within API Guidelines.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PRAW was designed to make following the `API guidelines
<https://github.com/reddit/reddit/wiki/API>`_ simple. It will not send a
request more often than every 2 seconds and it caches every page for 30
seconds. This can be modified in :ref:`configuration_files`.

The problem comes when we run multiple bots / scripts at the same time. PRAW
cannot share these settings between programs, so there will be at least 2
seconds between program A's requests and at least 2 seconds between program B's
requests, but combined their requests may come more often than every 2 seconds.
If you wish to run multiple program at the same time, either combine them into
one, ensure from within the programs (such as with message passing) that they
don't combined exceed the API guidelines, or :ref:`edit the configuration files
<configuration_files>` to affect how often a program can send a request.

All 3 bot problems will be covered more in-depth in a future tutorial.

For now, you can continue to the next part of our tutorial series:
:ref:`comment_parsing`.

The full Question-Discover program
----------------------------------

.. code-block:: python

    """"
    Question Discover Program

    Tutorial program for PRAW:
    See https://github.com/praw-dev/praw/wiki/Writing-A-Bot/
    """

    import time

    import praw

    r = praw.Reddit('PRAW related-question monitor by u/_Daimon_ v 1.0.'
                    'Url: https://praw.readthedocs.org/en/latest/'
                    'pages/writing_a_bot.html')
    r.login()
    already_done = []

    prawWords = ['praw', 'reddit_api', 'mellort']
    while True:
        subreddit = r.get_subreddit('learnpython')
        for submission in subreddit.get_hot(limit=10):
            op_text = submission.selftext.lower()
            has_praw = any(string in op_text for string in prawWords)
            # Test if it contains a PRAW-related question
            if submission.id not in already_done and has_praw:
                msg = '[PRAW related thread](%s)' % submission.short_link
                r.send_message('_Daimon_', 'PRAW Thread', msg)
                already_done.append(submission.id)
        time.sleep(1800)

.. _`r/learnpython`: http://www.reddit.com/r/learnpython
