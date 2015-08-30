.. _comment_parsing:

Comment Parsing
===============

A common task for many bots and scripts is to parse a submission´s comments. In
this tutorial we will go over how to do that as well as talking about comments
in general.

The Basics
----------

To illustrate the problems, we'll write a small script that replies
to any comment that contains the text "Hello". Our reply will contain the text
" world!".

Submission Comments
^^^^^^^^^^^^^^^^^^^

As usual, we start by importing PRAW and initializing our contact with
reddit.com. We also get a :class:`.Submission` object, where our script will
do its work.

>>> import praw
>>> r = praw.Reddit('Comment Scraper 1.0 by u/_Daimon_ see '
...                 'https://praw.readthedocs.org/en/latest/'
...                 'pages/comment_parsing.html')
>>> submission = r.get_submission(submission_id='11v36o')

After getting the :class:`.Submission` object we retrieve the comments and
look through them to find those that match our criteria. Comments are stored in 
the attribute :attr:`.comments` in a comment forest, with each tree root a
toplevel comment. E.g., the comments are organized just like when you visit the
submission via the website. To get to a lower layer, use :attr:`.replies` to
get the list of replies to the comment. Note that this may include
:class:`.MoreComments` objects and not just :class:`.Comment`.

>>> forest_comments = submission.comments

As an alternative, we can flatten the comment forest to get a unordered list
with the function :func:`praw.helpers.flatten_tree`. This is the easiest way to
iterate through the comments and is preferable when you don't care about
a comment's place in the comment forest. We don't, so this is what we are going
to use.

>>> flat_comments = praw.helpers.flatten_tree(submission.comments)

To find out whether any of those comments contains the text we are looking for,
we simply iterate through the comments.

>>> for comment in flat_comments:
...     if comment.body == "Hello":
...         reply_world(comment)

Our program is going to make comments to a submission. If it has bugs, then it
might flood a submission with replies or post gibberish. This is bad. So we
test the bot in `r/test <http://www.reddit.com/r/test>`_ before we let it loose
on a "real" subreddit. As it happens, our bot as described so far contains a
bug. It doesn't test if we've already replied to a comment before replying. We
fix this bug by storing the content_id of every comment we've replied to and
test for membership of that list before replying. Just like in
:ref:`writing_a_bot`.

The number of comments
^^^^^^^^^^^^^^^^^^^^^^

When we load a submission, the comments for the submission are also loaded, up
to a maximum, just like on the website. At reddit.com, this max is 200
comments. If we want more than the maximum number of comments, then we need
to replace the :class:`.MoreComments` with the :class:`.Comment`\s they represent.
We use the :meth:`.replace_more_comments` method to do this. Let's use this
function to replace all :class:`.MoreComments` with the :class:`.Comment`\s they
represent, so we get all comments in the thread.

>>> submission.replace_more_comments(limit=None, threshold=0)
>>> all_comments = submission.comments

The number of :class:`.MoreComments` PRAW can replace with a single API
call is limited. Replacing all :class:`.MoreComments` in a thread with many
comments will require many API calls and so take a while due to API delay between
each API call as specified in the
`api guidelines <https://github.com/reddit/reddit/wiki/API>`_.

Getting all recent comments to a subreddit or everywhere
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We can get comments made to all subreddits by using
:meth:`~praw.__init__.UnauthenticatedReddit.get_comments` and setting the
subreddit argument to the value "all".

>>> import praw
>>> r = praw.Reddit('Comment parser example by u/_Daimon_')
>>> all_comments = r.get_comments('all')

The results are equivalent to `/r/all/comments
<http://www.reddit.com/r/all/comments>`_.

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
^^^^^^^^^^^^^^^^

.. code-block:: python

    import praw

    r = praw.Reddit('Comment Scraper 1.0 by u/_Daimon_ see '
                    'https://praw.readthedocs.org/en/latest/'
                    'pages/comment_parsing.html')
    r.login('bot_username', 'bot_password')
    submission = r.get_submission(submission_id='11v36o')
    flat_comments = praw.helpers.flatten_tree(submission.comments)
    already_done = set()
    for comment in flat_comments:
        if comment.body == "Hello" and comment.id not in already_done:
            comment.reply(' world!')
            already_done.add(comment.id)

Navigating Trees
------------------

Comments are in trees, each submission has a comment forest. However with
some simple manipulation, we can manipulate

Special Comment Methods
^^^^^^^^^^^^^^^^^^^^^^^

Going up and down comment trees is useful for various scripts and is sometimes
needed, for replying to the parent or ancestral submitter, however natively
there aren't any easy solutions. Due to this PRAW has implemented ways to
do this from Comment objects.

Comment objects have the following special methods:

* ``get_tree()``
* ``get_submission()``
* ``get_context()``
* ``get_parent()``

PRAW can also return the various permalinks to the related "special" Submission
objects.

Please see :class:`.Comment` for more information as to how exactly to use
these methods

Parameter Passing and MoreComments Objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Any original parameters passed or functions done on the original Submission object
are not remembered when getting these new "special" Submission objects. For that
reason, you are allowed to both use the same ones when using the above methods or
even change them, if that pleases you.

Also, it is important to know that any original MoreComments objects that were
replaced are "unreplaced" when using the above methods. It is probably better to
do something like this:

>>> r = praw.Reddit('Reversing the reversing of MoreComments')
>>> submission = r.get_submission(submission_id='11v36o')
>>> submission.replace_more_comments(limit=None, threshold=0)
>>> for x in praw.helpers.flatten_tree(submission.comments):
...     new_parent = x.get_parent() # Reverses the replacement
...     new_parent.replace_more_comments(limit=None,
...                                      threshold=0) # Reverses the reversal
...     # do something with new_parent.comments

>>> r = praw.Reddit('Reversing the reversing parameters')
>>> submission = r.get_submission(submission_id='11v36o', comment_limit=20)
>>> for x in praw.helpers.flatten_tree(submission.comments):
...     new_parent = x.get_parent(comment_limt=20) # Repass comment_limit
...     # do something with new_parent.comments

You may not want to actually repass the paramaters, in which case, other than
what is explicitly mentioned in the methods, the defaults of the
:meth:`praw.UnauthenticatedReddit.get_submission` method are used.

[deleted] comments
------------------

When a comment is deleted, in most cases, that comment will not be viewable with a
browser nor the API. However, if a comment is made, and then a reply to that comment
is made, and *then* the original comment is deleted, that comment will have it's
``body`` and ``author`` attributes be ``NoneType`` via the API. The same goes with
removed comments, unless the authenticated account is a mod of the subreddit whose
comment's you are getting. If you are a mod, and said comments are removed comments,
they are left intact.

If a comment is made and then the account that left that comment is deleted, the
comment body is left intact, while the ``author`` attribute becomes ``NoneType``.