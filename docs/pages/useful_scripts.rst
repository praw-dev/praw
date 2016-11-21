.. _useful_scripts:

Useful Apps/Scripts
===================

Here are some scripts that people have contributed so far. Feel free to edit
this page to add in more.

`PRAWtools`_ by `BBoe <https://github.com/bboe>`_
    A collection of tools that utilize PRAW. Two current tools are ``modutils``
    a program useful to subreddit moderators, and ``subreddit_stats``, a tool
    to compute submission / comment statistics for a subreddit.

`prawoauth2`_ by `Avinash Sajjanshetty <https://github.com/avinassh>`_
    ``prawoauth2`` is a helper library for PRAW which makes writing Reddit bots/apps using 
    OAuth2 super easy, simple and fun.

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

`VideoLinkBot`_ by `u/shaggorama <http://www.reddit.com/user/shaggorama>`_
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

`RedditAgain`_ by `Karan Goel <https://github.com/karan>`_
    Migrate an old reddit account to a new one. Backs up existing content and
    submissions, and copies subscriptions to a new account.

`reddit-cloud`_ by `Paul Nechifor <https://github.com/paul-nechifor>`_
    Generates word clouds for submissions (or users), posts them to Imgur and
    the URL to reddit. It's what I run on
    `u/WordCloudBot2 <http://www.reddit.com/user/WordCloudBot2>`_.

`Reddit-to-Diigo-Copier`_ by `Doug <https://github.com/OdinsHat>`_
    Copies your reddit saved links to a Diigo account of your choice. Makes use
    of PRAW and the Diigo API.

`NetflixBot`_ by `Alan Wright <https://github.com/alanwright>`_
    Parses comments for calls and determines if a movie is availble for
    streaming on Netflix. Makes use of PRAW and the NetflixRouletteAPI. Run on
    `u/NetflixBot <http://www.reddit.com/user/NetflixBot>`_.

`RemindMeBot`_ by `Joey <https://github.com/Silver-->`_
    Called upon with the ``RemindMeBot!`` command on any subreddit, the user is
    able to set a reminder for themselves about the current thread or comment.
    The bot will then send them a private message with the date they specified.
    `u/RemindMeBot <http://www.reddit.com/user/RemindMeBot>`_.

`RedditRover`_ by `DarkMio <https://github.com/DarkMio>`_
    A plugin based Reddit Multi Bot Framework intended for new and advanced 
    programmers to host a wide variety of Reddit bots without mangling with
    all the ins and outs of Reddit, PRAW and API limitations. 

`Reddit Keyword Tracking Bot`_ by Jermell Beane
    <requires Kivy> A bot that will watch any subreddits and email you with
    updates when it finds words that matter to you.  settings are configured
    via a GUI making it easy for people who don't know how to edit python
    scripts.

`Reddit-Paper`_ by Cameron Gagnon.
    Command line interface program that will download the top 5 images from
    r/earthporn, r/spaceporn, etc. and set them as the computer's
    wallpaper. Currently only tested and used on Ubuntu, but more OS's coming
    soon.

`QR Codify <https://github.com/JstnPwll/QRCodify>`_ by JstnPwll
    Fetches username mentions and converts the comment data into a QR code. The
    code is then posted via ASCII characters as a followup comment.

`EVE Killmail Reddit Bot`_ by `ArnoldM904 <https://github.com/ArnoldM904>`_
    Searches for comments in /r/eve that contain zkillboard killmail links.
    Then replies to comments with web-scraped TL;DR of the information.
    
`ButtsBot`_ by `Judson Dunaway-Barlow <https://github.com/jadunawa>`_
    A silly bot that posts a picture of a (clothed) butt from the Astros team whenever somebody in the /r/Astros subreddit       uses any of a few certain keywords in a comment.

`GoodReads Bot`_ by `Avinash Sajjanshetty <https://github.com/avinassh>`_
    A bot which powers `/u/goodreadsbot <https://www.reddit.com/u/goodreadsbot>`_ on Reddit, posts information of a book whenever someone posts a link to Goodreads.

`Self-Destruct Bot`_ by `diceroll123 <https://github.com/diceroll123>`_
    Removes posts after a specified amount of time. (For time-sensitive posts.)

`Subtitle Bot`_ by `arrayofchar <https://github.com/arrayofchar>`_
    Finds youtube links and see if closed captioning (aka subtitle) is available. Formats subtitle into paragraphs based on  standard deviation of timestamp gaps. If subtitle is longer than Reddit comment limit, puts it in Pastebin.

**\<Your Script Here\>**
    Edit `this page on github <https://github.com/praw-dev/praw/blob/master/
    docs/pages/useful_scripts.rst>`_ to add your script to this list.


.. Please keep this list of links lexicographically sorted
.. _`AlienFeed`: https://github.com/jawerty/AlienFeed
.. _`ALTcointip`: https://github.com/vindimy/altcointip
.. _`AutoModerator`: https://github.com/Deimos/AutoModerator
.. _`Butcher bot`: https://github.com/xiphirx/Butcher-Bot
.. _`ButtsBot`: https://github.com/jadunawa/ButtsBot
.. _`EVE Killmail Reddit Bot`: https://github.com/ArnoldM904/EK_Reddit_Bot
.. _`GoodReads Bot`: https://github.com/avinassh/Reddit-GoodReads-Bot
.. _`Groompbot`: https://github.com/AndrewNeo/groompbot
.. _`NetflixBot`: https://github.com/alanwright/netflixbot
.. _`prawoauth2`: https://github.com/avinassh/prawoauth2
.. _`PRAWtools`: https://github.com/praw-dev/prawtools
.. _`Reddit Keyword Tracking Bot`:
     https://github.com/SwedishBotMafia/RScanBot.Gen
.. _`Reddit-Paper` : https://github.com/cameron-gagnon/reddit-paper
.. _`Reddit-to-Diigo-Copier`:
     https://github.com/OdinsHat/Reddit-to-Diigo-Copier
.. _`RedditAgain`: https://github.com/karan/RedditAgain
.. _`RedditRover` : https://github.com/DarkMio/RedditRover
.. _`RemindMeBot`: https://github.com/SIlver--/remindmebot-reddit
.. _`Self-Destruct Bot`: https://github.com/diceroll123/SelfDestructBot
.. _`Subtitle Bot`: https://github.com/arrayofchar/reddit_subtitle_bot
.. _`VideoLinkBot`: https://github.com/dmarx/VideoLinkBot
.. _`newsfrbot`: https://github.com/gardaud/newsfrbot
.. _`r/diablo flair infographic generator`:
     https://github.com/xiphirx/rdiablo-flair-infographic-generator
.. _`reddit-analysis`: https://github.com/rhiever/reddit-analysis
.. _`reddit-cloud`: https://github.com/paul-nechifor/reddit-cloud
.. _`u/xiphirx`: http://www.reddit.com/user/xiphirx
