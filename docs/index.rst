.. _main_page:

PRAW: The Python Reddit Api Wrapper
===================================

.. include:: ../README.rst
   :start-after: begin_description
   :end-before: end_description

Content Pages
-------------

.. toctree::
    :maxdepth: 1

    pages/getting_started
    pages/writing_a_bot
    pages/call_and_response_bot
    pages/comment_parsing
    pages/oauth
    pages/lazy-loading
    pages/multiprocess
    pages/contributor_guidelines
    pages/configuration_files
    pages/faq
    pages/changelog
    pages/code_overview
    pages/useful_scripts
    pages/exceptions

References And Other Relevant Pages
-----------------------------------

* `PRAW's Source Code <https://github.com/praw-dev/praw>`_
* `reddit's Source Code <https://github.com/reddit/reddit>`_
* `reddit's API Wiki Page <https://github.com/reddit/reddit/wiki/API>`_
* `reddit's API Documentation <https://www.reddit.com/dev/api>`_

* `reddit Markdown Primer
  <https://www.reddit.com/r/reddit.com/comments/6ewgt/reddit_markdown_primer_or
  _how_do_you_do_all_that/c03nik6>`_
* `reddit.com's FAQ <https://www.reddit.com/wiki/faq>`_
* `reddit.com's Status Twitterbot <https://twitter.com/redditstatus/>`_.
  Tweets when reddit goes up or down
* `r/changelog <https://www.reddit.com/r/changelog/>`_. Significant changes to
  reddit's codebase will be announced here in non-developer speak
* `r/redditdev <https://www.reddit.com/r/redditdev>`_. Ask questions about
  reddit's codebase, PRAW and other API clients here

.. include:: ../README.rst
   :start-after: begin_installation
   :end-before: end_installation

.. include:: ../README.rst
   :start-after: begin_support
   :end-before: end_support

.. include:: ../README.rst
   :start-after: begin_license
   :end-before: end_license

A Few Short Examples
--------------------

Note: These example are intended to be completed in order. While you are free
to skip down to what you want to accomplish, please check the previous examples
for any ``NameErrors`` you might encounter.

1. Import the package

    >>> import praw

#. Create the Reddit object (requires a user-agent):

    >>> r = praw.Reddit(user_agent='Test Script by /u/bboe')

#. Logging in:

    >>> r.login('username', 'password')

#. Send a message (requires login):

    >>> r.send_message('user', 'Subject Line', 'You are awesome!')

#. Mark all unread messages as read (requires login):

    >>> for msg in r.get_unread(limit=None):
    ...     msg.mark_as_read()

#. Get the top submissions for /r/python:

    >>> submissions = r.get_subreddit('python').get_top(limit=10)

#. Get comments from a given submission:

    >>> submission = next(submissions)
    >>> submission.comments

#. Comment on a submission (requires login):

    >>> submission.add_comment('text')

#. Reply to a comment (requires login):

    >>> comment = submission.comments[0]
    >>> comment.reply('test')

#. Voting (requires login):

    >>> # item can be a comment or submission
    >>> item.upvote()
    >>> item.downvote()
    >>> item.clear_vote()

#. Deleting (requires login):

    >>> # item can be a comment or submission
    >>> item.delete()

#. Saving a submission (requires login):

    >>> submission.save()
    >>> submission.unsave()

#. Create a SELF submission (requires login):

    >>> r.submit('reddit_api_test', 'submission title', text='body')

#. Create a URL submission (requires login):

    >>> r.submit('reddit_api_test', 'Google!', url='http://google.com')

#. Get user karma:

    >>> user = r.get_redditor('ketralnis')
    >>> user.link_karma
    >>> user.comment_karma

#. Get saved links (requires login):

    >>> r.user.get_saved()

#. Get content newer than a comment or submission's id:

    >>> r.get_subreddit('python').get_top(limit=None,
                                          place_holder=submission.id)

#. (Un)subscribe to a subreddit (requires login):

    >>> r.get_subreddit('python').subscribe()
    >>> r.get_subreddit('python').unsubscribe()

#. (Un)friend a user:

    >>> r.get_redditor('ketralnis').friend()
    >>> r.get_redditor('ketralnis').unfriend()

#. Create a subreddit:

    >>> r.create_subreddit(short_title='MyIncredibleSubreddit',
    ...                        full_title='my Incredibly Cool Subreddit',
    ...                        description='It is incredible!')

#. Get flair mappings for a particular subreddit (requires mod privileges):

    >>> item = next(r.get_subreddit('python').get_flair_list())
    >>> item['user']
    >>> item['flair_text']
    >>> item['flair_css_class']

#. Set / update user flair (requires mod privileges):

    >>> r.get_subreddit('python').set_flair('user', 'text flair', 'css-class')

#. Clear user flair (requires mod privileges):

    >>> r.get_subreddit('python').set_flair('user')

#. Bulk set user flair (requires mod privileges):

    >>> flair_mapping = [{'user':'user', 'flair_text':'dev'},
    ...                  {'user':'pyapitestuser3', 'flair_css_class':'css2'},
    ...                  {'user':'pyapitestuser2', 'flair_text':'AWESOME',
    ...                  'flair_css_class':'css'}]
    >>> r.get_subreddit('python').set_flair_csv(flair_mapping)

#. Add flair templates (requires mod privileges):

    >>> r.get_subreddit('python').add_flair_template(text='editable',
    ...                                              css_class='foo',
    ...                                              text_editable=True)

#. Clear flair templates (requires mod privileges):

    >>> r.get_subreddit('python').clear_flair_templates()

Useful Scripts
==============

`AutoModerator`_ by `Deimos <https://github.com/deimos>`_
    A bot for automating straightforward reddit moderation tasks and improving
    upon the existing spam-filter.


`ClockStalker <https://github.com/ClockStalker/clockstalker>`_
    Examines a redditor's posting history and creates `a comment with a nice
    activity overview
    <https://www.reddit.com/r/AskReddit/comments/129lyb/what_fact_about_reality_
    terrifies_you_or_gives/c6tbgd7?context=1>`_. ClockStalker uses an older
    version of PRAW, the ``reddit``, module. It should, but may not, work with
    the latest version of PRAW.

`DailyProgBot <https://github.com/nint22/DailyProgBot>`_
    A simple challenge-queue submission bot for r/DailyProgrammer. Users submit
    challenges through a Google Documents form, then the bot crawls said form,
    posting the appropriate challenge on the appropriate day of the week.

.. _`AutoModerator`: https://github.com/Deimos/AutoModerator
