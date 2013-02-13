.. _writing_a_bot:

Writing A Reddit Bot
====================

In the :ref:`getting_started` tutorial, we wrote a script to break down a
redditor's karma. In this we will write a bot, who differ from scripts in that
they are normally running continually and automate some task, that could be
performed by a user, such as posting, commenting or moderating. Writing bots
have some additional problems compared to scripts. We need to make sure they
keep working continually, that they don't unnecessarily perform the same task
twice and keep within `API Guidelines <https://github.com/reddit/reddit/wiki/
API>`_. This tutorial will introduce you to all three of the problems and show
how to use PRAW's and reddit's documentation.

The Problem
-----------

From time to time questions are submitted to reddit.com about PRAW, mellort's
depreciated fork and the reddit API in general. I want to be notified of these
submissions, so I can help the submitter. The bot will monitor the subreddits
`r/python <www.reddit.com/r/python>`_, `r/learnpython <www.reddit.com/r/
python>`_ and `r/redditdev <www.reddit.com/r/python>`_ and send me a private
message, whenever it detects a post with such a question.

We start by importing PRAW and logging in.

>>> import time
>>> import praw
>>> r = praw.Reddit('PRAW related-question monitor by u/_Daimon_ v 1.0. '
...                 'Url: https://github.com/praw-dev/'
...                 'praw/wiki/Writing-A-Bot/')
>>> r.login()
>>> already_done = [] # Ignore this for now

The next step is the main loop, where we look at each of the subreddit in turn.
For this tutorial we will implement a subset of the bot, that only look at the
submissions in `r/learnpython <www.reddit.com/r/python>`_ to make the example
code as clear as possible.

>>> while True:
>>> subreddit = r.get_subreddit('learnpython')
>>> for submission in subreddit.get_hot(limit=10):
        # Test if it contains a PRAW-related question

Finding what we need
^^^^^^^^^^^^^^^^^^^^

Now that we have the submissions, we need to see if they contain a PRAW-related
question. We are going to look at the text part of a submission to see if it
contains one of the strings "reddit api", "praw" or "mellort". I know which of
a submissions variables match the text part, but you might not. So we're going
to go through how you can find out stuff like this on your own.

Start the Python interpreter and compare the output with `this r/learnpython
<http://www.reddit.com/r/learnpython/comments/105aru/newbie_stripping_strings_
of_last_character/>`_ post.

>>> import praw
>>> r = praw.reddit('submission variables testing by /u/_daimon')
>>> submission = r.get_submission(submission_id = "105aru")
>>> print "vars: ", vars(submission)
{'domain': u'self.learnpython', '_comments_by_id': {u't1_c6akv1g': <praw.object
s.comment object at 0x00000000023f3cf8>, u't1_c6ak4rq': <praw.objects.comment
object at 0x00000000023f3e48>, u't1_c6akq4n': <praw.objects.comment object at
0x00000000023f3da0>, u't1_c6ailxt': <praw.objects.comment object at 0x000000000
23f3f98>, u't1_c6ailrj': <praw.objects.comment object at 0x00000000023f3ef0>,
u't1_c6aijmu': <praw.objects.comment object at 0x00000000023f3be0>}, '_popu¨
lated': true, 'banned_by': none, 'media_embed': {}, 'subreddit': <praw.objects.
subreddit object at 0x00000000023f3b38>, 'selftext_html': u'&lt;!-- sc_off --&g
t;&lt;div class="md"&gt;&lt;p&gt;update: thanks for the help. got fixed.&lt;/p&
gt;\n\n&lt;p&gt;i need to strip 3 strings in a list of 4 of their trailing comm
as to get my formatting right and to convert one of them (a number) to a float
but i'm confused on the syntax. also, i don&amp;#39;t know of an effici ent way
of completing the task; i was planning on stripping each of the three s trings
on a new line.&lt;/p&gt;\n\n&lt;pre&gt;&lt;code&gt;for line in gradefile :\n
linelist = string.split(line)\n    #strip linelist[0],[1], and [2] of co mmas\n
linelist = string.rstrip(linelist[0], &amp;quot;,&amp;quot;)\n&lt;/co
de&gt;&lt;/pre&gt;\n&lt;/div&gt;&lt;!-- sc_on --&gt;', 'selftext': u'update: th
anks for the help. got fixed.\n\ni need to strip 3 strings in a list of 4 of th
eir trailing commas to get my formatting right and to convert one of them (a nu
mber) to a float but i\m confused on the syntax. also, i don't know of an ef
ficient way of completing the task; i was planning on stripping each of the thr
ee strings on a new line.\n\n    for line in gradefile:\n        linelist = str
ing.split(line)\n        #strip linelist[0],[1], and [2] of commas\n lin elist
= string.rstrip(linelist[0], ",")', 'likes': none, 'link_flair_text': non e,
'id': u'105aru', 'clicked': false, 'title': u'newbie: stripping strings of l
ast character', 'num_comments': 6, '_comments_flat': none, '_orphaned': {}, 'sc
ore': 1, 'approved_by': none, 'over_18': false, '_all_comments': false, 'hidden
': false, 'thumbnail': u'', 'subreddit_id': u't5_2r8ot', 'edited': 1348083784.0
, 'link_flair_css_class': none, '_info_url': 'http://www.reddit.com/button_info
/', 'author_flair_css_class': none, 'reddit_session': <praw.reddit object at 0x
0000000001e310b8>, 'downs': 0, 'saved': false, 'is_self': true, '_comments': [<
praw.objects.comment object at 0x00000000023f3be0>, <praw.objects.comment objec
t at 0x00000000023f3ef0>, <praw.objects.comment object at 0x00000000023f3f98>],
'_underscore_names': none, 'permalink': u'http://www.reddit.com/r/learnpython/c
omments/105aru/newbie_stripping_strings_of_last_character/', 'name': u't3_105a
ru', 'created': 1348102969.0, 'url': u'http://www.reddit.com/r/learnpython/com
ments/105aru/newbie_stripping_strings_of_last_character/', 'author_flair_text'
: none, 'author': <praw.objects.redditor object at 0x00000000023f3c18>, 'creat
ed_utc': 1348077769.0, 'media': none, 'num_reports': none, 'ups': 1}
>>>
>>>
>>> dir(submission) ['__class__', '__delattr__', '__dict__', '__doc__',
'__eq__', '__format__', '__ getattr__', '__getattribute__', '__hash__',
'__init__', '__module__', '__new__' , '__reduce__', '__reduce_ex__',
'__repr__', '__setattr__', '__sizeof__', '__st r__', '__subclasshook__',
'__unicode__', '__weakref__', '_all_comments', '_comm ents', '_comments_by_id',
'_comments_flat', '_get_json_dict', '_info_url', '_in sert_comment',
'_orphaned', '_populate', '_populated', '_replace_more_comments' ,
'_underscore_names', '_update_comments', 'add_comment', 'all_comments', 'all_
comments_flat', 'approve', 'approved_by', 'author', 'author_flair_css_class', '
author_flair_text', 'banned_by', 'clear_vote', 'clicked', 'comments', 'comments
_flat', 'content_id', 'created', 'created_utc', 'delete', 'distinguish', 'domai
n', 'downs', 'downvote', 'edit', 'edited', 'from_api_response', 'get_info', 'hi
dden', 'hide', 'id', 'is_self', 'likes', 'link_flair_css_class', 'link_flair_te
xt', 'mark_as_nsfw', 'media', 'media_embed', 'name', 'num_comments', 'num_repor
ts', 'over_18', 'permalink', 'reddit_session', 'refresh', 'remove', 'report', '
save', 'saved', 'score', 'selftext', 'selftext_html', 'set_flair', 'short_link'
, 'subreddit', 'subreddit_id', 'thumbnail', 'title', 'undistinguish', 'unhide',
'unmark_as_nsfw', 'unsave', 'ups', 'upvote', 'url', 'vote']

``vars`` contain the objects attributes and the values they contain. For
instance we can see that it has the variable ``title`` with the value
``u'Newbie: stripping strings of last character``. ``dir`` returns the names in
the local scope. You can also use ``help`` for introspection, if you wish to
generate a longer help page.  Worth noting is that PRAW contains a lot of
property-decorated functions eg.  functions that are used as variables. So if
you're looking for something that behaves like a variable, it might not be in
vars. One of these is ``short_link``, which returns a much shorter url to the
submission and is called as a variable.

Another way of finding out how a Reddit page is translated to variables is to
look at the .json version of that page. Just append .json to a reddit url to
look at the json version, such as the `previous r/learnpython post
<http://www.reddit.com/r/learnpython/comments/105aru/newbie_stripping_strings_
of_last_character/.json>`_. The variable name reddit uses for a variable is
almost certainly the same PRAW uses.

The 3 Bot Problems.
-------------------

Not Doing The Same Work twice.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From the information we gained in the previous section, we see that the text
portion of a submission is stored in the variable ``selftext``. So we test if
any of the strings are within the ``selftext``, and if they are the bot sends
me a message. But I should only ever receive a single message per submission.
So we need to maintain a list of the submissions I've already been messaged
about.  Each ``Thing`` has a unique ID, so we simply store the used ones in a
list and check for membership before mailing. Finally we sleep 30 mins and
restart the main loop.

>>> prawWords = ['praw', 'reddit_api', 'mellort']
>>> op_text = submission.selftext.lower()
>>> has_praw = any(string in op_text for string in prawWords)
>>> if submission.id not in already_done and has_praw:
...     msg = '[PRAW related thread](%s)' % submission.short_link
...     r.user.send_message('_Daimon_', msg)
...     already_done.append(submission.id)
>>> time.sleep(1800)

Running Continually.
^^^^^^^^^^^^^^^^^^^^

reddit.com is going to crash and other problems will be met. That's a fact of
life. Good bots should be able to take this into account and either exit
gracefully or outwait the problem. This is a simple bot, where the loss of all
data isn't very problematic. So for now we're simply going to accept that it
will crash with total loss of data at the first problem encountered.

Keeping Within API Guidelines.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PRAW was designed to make following the `API guidelines
<https://github.com/reddit/reddit/wiki/API>`_ simple. It will not send a
request more often than every 2 seconds and it caches every page for 30
seconds. This can be modified in :ref:`configuration_files`

The problem comes when we run multiple bots / scripts at the same time, PRAW
cannot share these settings between programs. So there will be at least 2
seconds between program A's requests and at least 2 seconds between program B's
requests, but combined their requests may come more often than every 2 seconds.
If you wish to run multiple program at the same time. Either combine them into
one, ensure from within the programs (such as with message passing) that they
don't combined exceed the API guidelines or :ref:`edit the configuration files
<configuration_files>` to affect how often a program can send a request.

All 3 bot problems will be covered more in-depth in a future tutorial.

For now, you can continue to the next part of our tutorial series.
:ref:`comment_parsing`

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
                    'Url: https://github.com/praw-dev/'
                    'praw/wiki/Writing-A-Bot/')
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
                r.user.send_message('_Daimon_', msg)
                already_done.append(submission.id)
        time.sleep(1800)
