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
    pages/changelog

References And Other Relevant Pages
-----------------------------------

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

Extra usage info
----------------

* All of the listings (list of stories on subreddit, etc.) are generators,
  *not* lists. If you need them to be lists, an easy way is to call ``list()``
  with your variable as the argument.
* The default limit for fetching Things is 25. You can change this with the
  ``limit`` param. If you don't want a limit, set ``limit=None``. This will
  return almost 1000 entires and then stop due to limitations in reddits
  database.


Example Applications/Scripts
----------------------------

* `BBoe\'s PRAWtools <https://github.com/praw-dev/prawtools>`_ A collection of
  tools that utilize PRAW. Two current tools are ``modutils`` a program useful
  to subreddit modterators, and ``subreddit_stats``, a tool to compute
  submission / comment statistics for a subreddit.
* `Deimos's AutoModerator <https://github.com/Deimos/AutoModerator>`_, a bot
  for automating straightforward reddit moderation tasks and improving upon the
  existing spam-filter.
* `r.doqdoq <http://r.doqdoq.com/>`_, a website that displays reddit stories
  under the guise of Python or Java code. Source available on
  `bitbucket <https://bitbucket.org/john2x/rdoqdoq>`_.
* `Reddit Notifier <https://github.com/nemec/reddit-notify>`_ for Gnome3.
  Integrates with Unity and Gnome Shell to display new Reddit mail as it
  arrives.
* `Link Unscripter <https://github.com/sparr/reddit-link-unscripter>`_, a bot
  for replying to posts <and comments, eventually>`_ that contain
  javascript-required links, to provide non-javascript alternatives
* `ClockStalker <https://github.com/ClockStalker/clockstalker>`_. Examines a
  redditor's posting history and creates `a comment with a nice activity
  overview
  <http://www.reddit.com/r/AskReddit/comments/129lyb/what_fact_about_reality_
  terrifies_you_or_gives/c6tbgd7?context=1>`_. ClockStalker uses an older
  version of PRAW, the ``reddit``, module. It should, but may not, work with
  the latest version of PRAW.
* `Butcher bot <https://github.com/xiphirx/Butcher-Bot>`_ by
  `u/xiphirx <http://www.reddit.com/user/xiphirx>`_ handles routine tasks on
  `r/Diablo <http://www.reddit.com/r/diablo>`_ such as the removal of
  images/memes and bandwagon-esque titles
* `r/diablo flair infographic generator
  <https://github.com/xiphirx/rdiablo-flair-infographic-generator>`_ by
  `u/xiphirx <http://www.reddit.com/user/xiphirx>`_ creates beautiful
  `infographics <http://i.imgur.com/smqWx.jpg>`_.
* `Groompbot <https://github.com/AndrewNeo/groompbot>`_ by
  `u/AndrewNeo <http://www.reddit.com/user/AndrewNeo>`_ posts new videos from
  YouTube to a subreddit.
* `newsfrbot <https://github.com/gardaud/newsfrbot>`_ by `u/keepthepace
  <http://www.reddit.com/user/keepthepace>`_ parses RSS feeds from some major
  french publications and posts them to relevant subreddits.
* `reddit-modbot <https://github.com/rasher/reddit-modbot>`_ is a relatively
  lightweight script for automating reddit moderating tasks. It was written as
  a simpler alternative to `AutoModerator by Deimos
  <https://github.com/Deimos/AutoModerator>`_.
* `reddit-giveaway-bot <https://github.com/nemec/reddit-giveaway-bot>`_ is a
  bot that automatically manages giveaways <such as giving out product keys to
  the first N commenters>`_.
* `DailyProgBot <https://github.com/nint22/DailyProgBot>`_ is a simple
  challenge-queue submission bot for r/DailyProgrammer. Users submit challenges
  through a Google Documents form, then the bot crawls said form, posting the
  appropriate challenge on the appropriate day of the week.
* `DailyPromptBot <http://hg.arenthil.net/dailypromptbot>`_. The management bot
  for the `r/TheDailyPrompt <www.reddit.com/r/TheDailyPrompt>`_ reddit
  community.  Main functions include managing a queue of prompts, posting
  prompts daily, and posting suggestion threads weekly.
* `VideoLinkBot <https://github.com/dmarx/VideoLinkBot>`_ by
  `u/shaggorama <http://www.reddit.com/u/shaggorama>`_, a bot that aggregates
  video links in a response comment where multiple videos links appear in reply
  to a submission (uses a slightly out-of-date version of PRAW, currently
  requires Submission.all_comments_flat).
* \<Your Script Here\> Edit this page to add it yourself.

Note: The following use very outdated versions of the API. Don't expect them
to work with the latest version.

* A `comment tracker <https://github.com/mellort/reddit_comment_tracker>`_,
  that repeatedly looks at new reddit comments and can take an action if they
  meet a specified condition. The example use I gave is replying with an
  automated message if the body of a comment contains a certain word. <Novelty
  accounts, anyone?>`_
* An `account cloner <https://github.com/mellort/reddit_account_cloner>`_ that
  given two logins and passwords, it will transfer all of the saved links and
  subscribed subreddits from the first account to the second.
* A `comment generator <https://github.com/mellort/reddit_comment_bot>`_ that
  pulls comments from reddit, puts them in a Markov chain, and periodically
  outputs random statuses. The statuses can be viewed `here
  <http://identi.ca/redditbot/all>`_.
