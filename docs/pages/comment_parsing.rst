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
them to find those that match our criteria. Comments are stored in the
attribute ``comments`` in a comment forest, with each tree root a toplevel
comment. Eg. the comments are organised just like when you visit the submission
via the webend. To get to a lower layer, use ``replies`` to get the list of
replies to the comment. Note that this may include ``MoreComment`` objects and
not just ``Comments``.

>>> forest_comments = submission.comments

As an alternative, we can flatten the comment forest to get a unordered list
with the function ``praw.helpers.flatten_tree``. This is the easiest way to
iterate through the comments and is preferable when you don't don't care about
a comments place in the comment forest. We don't, so this is what we are going
to use.

>>> flat_comments = praw.helpers.flatten_tree(submission.comments)

To find out whether any of those comments contains the text we are looking for,
we simply iterate through the comments.

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

The number of comments
----------------------

When we load a submission, we load comments up to a max alongside it. Just like
on the webend. At reddit.com, this max is 200 comments. If we want more than
these comments, then we need to replace the MoreComments with the Comments they
represent. We use the ``replace_more_comments`` method to do this. Let's use
this function to replace all MoreComments with the comments they represent, so
we get all comments in the thread.

>>> submission.replace_more_comments(limit=None, threshold=0)
>>> all_comments = s.comments

It's limited how many MoreComments PRAW can replace with a single API call.
Replacing all MoreComments in a thread with many comments will require many API
calls and so take a while due to API delay between each API call as specified
in the `api guidelines <https://github.com/reddit/reddit/wiki/API>`_.

Getting all recent comments to a subreddit or everywhere
--------------------------------------------------------

We can get all comments made anywhere with ``get_all_comments()``.

>>> import praw
>>> r = praw.Reddit('Comment parser example by u/_Daimon_')
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

The full program
----------------

.. code-block:: python

    import praw

    r = praw.Reddit('Comment Scraper 1.0 by u/_Daimon_ see github.com/'
                    'praw-dev/praw/wiki/Comment-Parsing')
    r.login('bot_username', 'bot_password')
    submission = r.get_submission(submission_id='11v36o')
    flat_comments = praw.helpers.flatten_tree(submission.comments_flat)
    already_done = []
    for comment in flat_comments:
        if comment.body == "Hello" and comment.id not in already_done:
            comment.reply(' world!')
            already_done.append(comment.id)

