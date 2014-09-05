.. _useful_scripts:

Useful Apps/Scripts
===================

Here are some scripts that people have contributed so far. Feel free to edit
this page to add in more.

`PRAWtools`_ by `BBoe <https://github.com/bboe>`_
    A collection of tools that utilize PRAW. Two current tools are ``modutils``
    a program useful to subreddit moderators, and ``subreddit_stats``, a tool
    to compute submission / comment statistics for a subreddit.

`AutoModerator`_ by `Deimos <https://github.com/deimos>`_
    A bot for automating straightforward reddit moderation tasks and improving
    upon the existing spam-filter.

`r.doqdoq <https://bitbucket.org/john2x/rdoqdoq>`_
    A website that displays reddit stories under the guise of Python or Java
    code.

`reddit Notifier <https://github.com/nemec/reddit-notify>`_ for Gnome3
    Integrates with Unity and Gnome Shell to display new reddit mail as it
    arrives.

`Link Unscripter <https://github.com/sparr/reddit-link-unscripter>`_
    A bot for replying to posts <and comments, eventually> that contain
    javascript-required links to provide non-javascript alternatives.

`ClockStalker <https://github.com/ClockStalker/clockstalker>`_
    Examines a redditor's posting history and creates `a comment with a nice
    activity overview
    <http://www.reddit.com/r/AskReddit/comments/129lyb/what_fact_about_reality_
    terrifies_you_or_gives/c6tbgd7?context=1>`_. ClockStalker uses an older
    version of PRAW, the ``reddit``, module. It should, but may not, work with
    the latest version of PRAW.

`Butcher bot`_ by `u/xiphirx <http://www.reddit.com/user/xiphirx>`_
    Handles routine tasks on `r/Diablo <http://www.reddit.com/r/diablo>`_ such
    as the removal of images/memes and bandwagon-esque titles.

`r/diablo flair infographic generator`_ by `u/xiphirx`_
    Creates beautiful `infographics <http://i.imgur.com/smqWx.jpg>`_.

`Groompbot`_ by `u/AndrewNeo <http://www.reddit.com/user/AndrewNeo>`_
    Posts new videos from YouTube to a subreddit.

`newsfrbot`_ by `u/keepthepace <http://www.reddit.com/user/keepthepace>`_
    Parses RSS feeds from some major french publications and posts them to
    relevant subreddits.

`reddit-modbot <https://github.com/rasher/reddit-modbot>`_
    A relatively lightweight script for automating reddit moderating tasks.  It
    was written as a simpler alternative to `AutoModerator`_ by Deimos.

`reddit-giveaway-bot <https://github.com/nemec/reddit-giveaway-bot>`_
    A bot that automatically manages giveaway. One feature gives out product
    keys to the first N commenters.

`DailyProgBot <https://github.com/nint22/DailyProgBot>`_
    A simple challenge-queue submission bot for `r/DailyProgrammer
    <http://www.reddit.com/r/Dailyprogrammer>`_. Users submit challenges
    through a Google Documents form, then the bot crawls said form, posting the
    appropriate challenge on the appropriate day of the week.

`DailyPromptBot <http://hg.arenthil.net/dailypromptbot>`_
    The management bot for the `r/TheDailyPrompt
    <http://www.reddit.com/r/TheDailyPrompt>`_ reddit community. Main
    functions include managing a queue of prompts, posting prompts daily, and
    posting suggestion threads weekly.

`VideoLinkBot`_ by `u/shaggorama <http://www.reddit.com/u/shaggorama>`_
    A bot that aggregates video links in a response comment where multiple
    videos links appear in reply to a submission (uses a slightly out-of-date
    version of PRAW, currently requires ``Submission.all_comments_flat``).

`reddit-analysis`_ by `u/rhiever <http://www.reddit.com/user/rhiever>`_
    Scrapes a specific subreddit or user and prints out all of the
    commonly-used words in the past month. Contains a data file containing a
    list of words that should be considered common.

`AlienFeed`_ by `u/Jawerty <http://www.reddit.com/user/Jawerty>`_
    AlienFeed is a command line application made for displaying and interacting
    with reddit submissions. The client can return a list containing the top
    submissions in a subreddit, and even open the links up if you'd like.

`ALTcointip`_ by `u/im14 <http://www.reddit.com/user/im14>`_
    ALTcointip bot allows redditors to gift (tip) various cryptocoins
    (Litecoin, PPCoin, Namecoin, etc) to each other as a way of saying thanks.

`RedditAgain`_ by `Karan Goel <http://www.github.com/thekarangoel>`_
    Migrate an old reddit account to a new one. Backs up existing content and
    submissions, and copies subscriptions to a new account.

`reddit-cloud`_ by `Paul Nechifor <http://www.github.com/paul-nechifor>`_
    Generates word clouds for submissions (or users), posts them to Imgur and
    the URL to reddit. It's what I run on
    `u/WordCloudBot2 <http://www.reddit.com/user/WordCloudBot2>`_.

`Reddit-to-Diigo-Copier`_ by `Doug <http://www.github.com/OdinsHat>`_
    Copies your reddit saved links to a Diigo account of your choice. Makes use
    of PRAW and the Diigo API.

`NetflixBot <http://github.com/alanwright/netflixbot>`_ by `Alan Wright <http://www.github.com/alanwright>`_
    Parses comments for calls and determines if a movie is availble for
    streaming on Netflix. Makes use of PRAW and the NetflixRouletteAPI. Run on
    `u/NetflixBot <http://www.reddit.com/user/NetflixBot>`_.

`RemindMeBot <https://github.com/SIlver--/remindmebot-reddit>`_ by `Joey <http://www.github.com/Silver-->`_
    Called upon with the ``RemindMeBot!`` command on any subreddit, the user is
    able to set a reminder for themselves about the current thread or comment.
    The bot will then send them a private message with the date they specified.
    `u/RemindMeBot <http://www.reddit.com/user/RemindMeBot>`_.

`Massdrop Multi Bot <http://github.com/darkmio/Massdrop-Reddit-Bot>`_
   A bot which made Massdrop available for everyone and then grew into an
   assortment of different fixes for links that regularly get mistakenly used,
   like Gfycat, Massdrop and Subreddit-Names in titles.
   
`Reddit Keyword Tracking Bot <https://github.com/SwedishBotMafia/RScanBot.Gen>`_ by Jermell Beane
    <requires Kivy> A bot that will watch any subreddits and email you with updates when it finds words that matter to you.
    settings are configured via a GUI making it easy for people who don't know how to edit python scripts. 

**\<Your Script Here\>**
    Edit `this page on github <https://github.com/praw-dev/praw/blob/master/
    docs/pages/useful_scripts.rst>`_ to add your script to this list.

**Note:** The following use very outdated versions of the API. Don't expect
them to work with the latest version.

`comment tracker <https://github.com/mellort/reddit_comment_tracker>`_
    Repeatedly looks at new reddit comments and can take an action if they meet
    a specified condition. The example use I gave is replying with an automated
    message if the body of a comment contains a certain word. <Novelty
    accounts, anyone?>

`account cloner <https://github.com/mellort/reddit_account_cloner>`_
    Given two logins and passwords, it will transfer all of the saved links and
    subscribed subreddits from the first account to the second.

`comment generator <https://github.com/mellort/reddit_comment_bot>`_
    Pulls comments from reddit, puts them in a Markov chain, and periodically
    outputs random statuses. The statuses can be viewed `here
    <http://identi.ca/redditbot/all>`_.

.. _`AlienFeed`: https://github.com/jawerty/AlienFeed
.. _`ALTcointip`: https://github.com/vindimy/altcointip
.. _`AutoModerator`: https://github.com/Deimos/AutoModerator
.. _`Butcher bot`: https://github.com/xiphirx/Butcher-Bot
.. _`Groompbot`: https://github.com/AndrewNeo/groompbot
.. _`PRAWtools`: https://github.com/praw-dev/prawtools
.. _`reddit-analysis`: https://github.com/rhiever/reddit-analysis
.. _`RedditAgain`: https://github.com/thekarangoel/RedditAgain
.. _`reddit-cloud`: https://github.com/paul-nechifor/reddit-cloud
.. _`Reddit-to-Diigo-Copier`:
    http://www.github.com/OdinsHat/Reddit-to-Diigo-Copier
.. _`r/diablo flair infographic generator`:
    https://github.com/xiphirx/rdiablo-flair-infographic-generator
.. _`VideoLinkBot`: https://github.com/dmarx/VideoLinkBot
.. _`newsfrbot`: https://github.com/gardaud/newsfrbot
.. _`u/xiphirx`: http://www.reddit.com/user/xiphirx
