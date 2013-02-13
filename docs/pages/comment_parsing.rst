.. _comment_parsing:

Comment Parsing
===============

A common task for many bots and scripts is to parse a submission´s comments. In
this tutorial we will go over how to do that as well as talking about comments
in general. To illustrate the problems, we'll write a small script that replies
to any comment that contains the text "Hello". Our reply will contain the text
" world!".

Submission Comments
-------------------

As usual, we start by importing PRAW and initializing our contact with
reddit.com. We also get a submission object, where our script will do it's
work.

>>> import praw
>>> r = praw.Reddit('Comment Scraper 1.0 by u/_Daimon_ see github.com/'
...                 'praw-dev/praw/wiki/Comment-Parsing')
>>> submission = r.get_submission(submission_id='11v36o')

After getting the submission object we retrieve the comments and look through
them to find those that match our criteria. There are two ways of retrieving
comments. Either we use ``comments`` to get the comments as an forest, where
each tree root is a toplevel comment. Eg. the comments are organised just like
when you visit the submission via the webend. To get to a lower layer, use
``replies`` to get the list of replies to the comment. Note that this may
include ``MoreComment`` objects and not just ``Comments``.

>>> forest_comments = submission.comments

The alternative way is to use ``comments_flat`` to get the comments in a flat
unnested list. This is the easiest way to iterate through the comments and is
preferable when you don't don't care about a comments place in the comment
forest. We don't, so this is what we are going to use.

>>> flat_comments = submission.comments_flat

To find out whether any of those comments contains the text we are looking for,
we simply iterate through the comments created by the generator and see if they
verify our criteria.

>>> for comment in flat_comments:
...     if comment.body == "Hello":
...         reply_world(comment)

Our program is going to make comments to a submission. If it has bugs, then it
might flood a submission with replies or post gibberish. This is bad. So we
test the bot in `r/test <www.reddit.com/r/test>`_ before we let it loose on a
"real" subreddit. As it happens, our bot as described so far contains a bug. It
doesn't test if we've already replied to a comment before replying. We fix this
bug by storing the content_id of every comment we've replied to and test for
membership of that list before replying. Just like in :ref:`writing_a_bot`.
The full program with this fix is included at the bottom of this page. You're
very welcome to try and test it out.

The number of comments
----------------------

The number of comments loaded alongside the loading of a submission is limited,
just like on the webend. For reddit.com the maximum number of comments that can
be loaded is 500 for an unauthenticated session / regular account and 1500 for
a gold account. The default number loaded is 200. These settings are defined in
``praw.in`` and can be modified as described in :ref:`configuration_files`.

Both ``comments`` and ``comments_flat`` only returns the comments that have
been loaded so far. Use  ``all_comments`` or ``all_comments_flat`` to load and
return all comments. ``all_comments`` returns the comments in a comment forest
just like ``comments``. ``all_comments_flat`` returns them in a list like
``comments_flat``.  Once either of these functions have been run, both
``comments`` and ``comments_flat`` will return all the submissions comments.

Note that getting all comments to a submission may take a very long time to
execute as each MoreComment requires an api call to expand, and each api call
must be separated by 2 seconds as specified in the `api guidelines
<https://github.com/reddit/reddit/wiki/API>`_. PRAW comes with an upper limit
on the number of MoreComments that can expanded with a ``all_comments`` or
``all_comments_flat`` call to prevent your program hanging too long. The limit
can be modified in ``praw.ini``.

The full program
----------------

.. code-block:: python

    import praw

    r = praw.Reddit('Comment Scraper 1.0 by u/_Daimon_ see github.com/'
                    'praw-dev/praw/wiki/Comment-Parsing')
    r.login('bot_username', 'bot_password')
    submission = r.get_submission(submission_id='11v36o')
    flat_comments = submission.comments_flat
    already_done = []
    for comment in flat_comments:
        if comment.body == "Hello" and comment.id not in already_done:
            comment.reply(' world!')
            already_done.append(comment.id)

Getting all recent comments to a subreddit or everywhere
--------------------------------------------------------

We can get all comments made anywhere with ``get_all_comments()``.

>>> import praw
>>> r = praw.Reddit('Comment parser')
>>> all_comments = r.get_all_comments()

The results are equivalent to `/comments <http://www.reddit.com/comments>`_.

We can also choose to only get the comments from a specific subreddit. This is
much simpler than getting all comments made to a reddit and filtering them. It
also reduces the load on the reddit.

>>> subreddit = r.get_subreddit('python')
>>> subreddit_comments = subreddit.get_comments()

The results are equivalent to
`r/python/comments <http://www.reddit.com/r/python/comments>`_.

You can use multi-reddits to get the comments from multiple subreddits.

>>> multi_reddits = r.get_subreddit('python+learnpython')
>>> multi_reddits_comments = multi_reddits.get_comments()

Which is equivalent to `r/python+learnpython/comments
<http://www.reddit.com/r/learnpython+python/comments>`_.
