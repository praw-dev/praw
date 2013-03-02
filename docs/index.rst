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
    pages/comment_parsing
    pages/oauth
    pages/contributor_guidelines
    pages/configuration_files
    pages/faq
    pages/changelog
    pages/code_overview
    pages/useful_scripts

References And Other Relevant Pages
-----------------------------------

* `PRAW's Source Code <https://github.com/praw-dev/praw>`_
* `Reddit's Source Code <https://github.com/reddit/reddit>`_
* `Reddit's API Wiki Page <https://github.com/reddit/reddit/wiki/API>`_
* `Reddit's API Documentation <http://www.reddit.com/dev/api>`_

* `Reddit Markdown Primer
  <http://www.reddit.com/r/reddit.com/comments/6ewgt/reddit_markdown_primer_or
  _how_do_you_do_all_that/c03nik6>`_
* `Reddit.com's FAQ <http://www.reddit.com/help/faq>`_
* `Reddit.com's Status Twitterbot <https://twitter.com/redditstatus/>`_.
  Tweets when Reddit goes up or down
* `r/changelog <http://www.reddit.com/r/changelog/>`_. Significant changes to
  Reddit's codebase will be announced here in non-developer speak
* `r/redditdev <http://www.reddit.com/r/redditdev>`_. Ask questions about
  Reddit's codebase, PRAW and other API clients here

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

#. Create the Reddit object (requires a user agent):

    >>> r = praw.Reddit(user_agent='example')

#. Logging in:

    >>> r.login('username', 'password')

#. Send a message (requires login):

    >>> r.send_message('bboe', 'Subject Line', 'You are awesome!')

#. Mark all unread messages as read (requires login):

    >>> for msg in r.get_unread(limit=None):
    ...     msg.mark_as_read()

#. Get the top submissions for /r/python:

    >>> submissions = r.get_subreddit('python').get_top(limit=10)

#. Get comments from a given submission:

    >>> submission = submissions.next()
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

    >>> item = r.get_subreddit('python').get_flair_list().next()
    >>> item['user']
    >>> item['flair_text']
    >>> item['flair_css_class']

#. Set / update user flair (requires mod privileges):

    >>> r.get_subreddit('python').set_flair('bboe', 'text flair', 'css-class')

#. Clear user flair (requires mod privileges):

    >>> r.get_subreddit('python').set_flair('bboe')

#. Bulk set user flair (requires mod privileges):

    >>> flair_mapping = [{'user':'bboe', 'flair_text':'dev'},
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

