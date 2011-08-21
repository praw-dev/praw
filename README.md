Introduction
------------

This is a Python wrapper for Reddit's API, aiming to be as easy to use as possible. 
Here's a quick peek, getting the first 10 stories from the 'hot' section of the 'opensource' subreddit.

    import reddit
    r = reddit.Reddit(user_agent="my_cool_application")
    stories = r.get_subreddit('opensource').get_hot(limit=5)
    list(stories)

this displays

    [<Submission: 1 :: OpenFOAM: Open Source Computational Fluid Dynamics>,
     <Submission: 9 :: My new open source project, Bunchify>,
     <Submission: 93 :: Arrested while contributing to OpenStreetMap>,
     <Submission: 27 :: DK: 25,000 hospital staff Copenhagen region to use open source office suite >,
     <Submission: 24 :: Eclipse online>]


Install
-------
You can install via `pip` 

    pip install reddit

Or via `setup.py`

    python setup.py install


A Few Short Examples
--------------------

1. Logging in:

        r.login(user="username", password="password")

2. Get top stories for r/python:

        stories = r.get_subreddit("python").get_top(limit=10)

3. Voting (requires login):

        story.upvote()
        story.downvote()

4. Get user karma:

        ketralnis = r.get_redditor("ketralnis")
        print ketralnis.link_karma, ketralnis.comment_karma

5. Comment on story (requires login):

        story.comment("text")

6. Reply to comment (requires login):

        comment.reply("test")

7. Get my saved links (requires login):

        r.get_saved_links()

8. Retrieve the urls of my saved links:

        saved_urls = [saved_link.url for saved_link in r.get_saved_links()]

9. Get comments from all reddits (i.e. http://www.reddit.com/comments:

        r.get_comments(limit=25)

10. Get content newer than a comment or submission's id:

        r_python.get_top(limit=None, place_holder=submission.id)

11. Comments from a given submission:

        submission.comments

12. Subscribe to a subreddit:

        subreddit.subscribe()

13. Save a submission:

        submission.save()
        
14. Delete a submission:

        submission.delete()

15. Create a subreddit:

        s = r.create_subreddit(short_title="MyIncredibleSubreddit", \
                               full_title="my Incredibly Cool Subreddit", \
                               description="It's incredible!)

16. Friend a user:

        r.get_redditor("ketralnis").friend()

Other (more involved) examples can be found [here](http://www.github.com/mellort/reddit_api/blob/master/EXAMPLES.md).

Extra usage info
----------

* All of the listings (list of stories on subreddit, etc.) are
  generators, *not* lists. If you need them to be lists, an easy way is
    to call `list()` with your variable as the argument.
* The default limit for fetching stories is 25. You can change this with
  the `limit` param. If you don't want a limit, set `limit=None`. This
    will return an infinite generator that will continue fetching
    stories until reddit hiccups (I wouldn't expect more than ~300
    stories). 
* 

Example Applications/Scripts
----------------------------

Note: these all use very outdated versions of the API. 
Don't expect them to work with the latest version.
I recommend using them as reference only.

* A [comment tracker](http://github.com/mellort/reddit_comment_tracker/blob/master/comment_tracker.py), which repeatedly looks at new Reddit comments and can take an action if they meet a specified condition. The example use I gave is replying with an automated message if the body of a comment contains a certain word. (Novelty accounts, anyone?)
* An [account cloner](http://github.com/mellort/reddit_account_cloner/blob/master/account_cloner.py). Given two logins and passwords, it will transfer all of the saved links and subscribed subreddits from the first account to the second.
* A [comment generator](http://github.com/mellort/reddit_comment_bot): it pulls comments from Reddit, puts them in a Markov chain, and periodically outputs random statuses. The statuses can be viewed [here](http://identi.ca/redditbot/all).

I hope that this wrapper allows for many more quick and useful applications to be made!

Dependencies
------------

* [setuptools](http://pypi.python.org/pypi/setuptools) is required to install reddit_api.

FAQ
------------

> Why is everything so slow?

Usually that has to do with how fast reddit is responding at the moment. Check
the site, see if it's responding quicker when accessing it in your browser.
Otherwise, we respect the "no more than one API call per two seconds" rule, so if you're trying to do a bunch of quick requests in succession you're going to be spaced out to one call per second. If you're having a specific issue besides something covered by one of those two things, please let us know (or file a ticket) and we'll check it out.

> I want to change the sort/time options for a given listing. How do I
> do that?

This currently isn't a part of the wrapper, but the `_get_sorter` method
in `helpers.py` is exactly what you want. The parameters you want to
change are `sort` and `time`. I'll add this to the wrapper shortly.

> I want a new feature!

File an enhacement request via github issues.

> Something doesn't work. What gives?

File an issue, I'll look into it.

> I want to help develop, but I'm lost. 

Send me a github message. I can help you get aquainted with the code
base, and maybe we can write a wiki page for others, too.

Pending features
----------------

Feel free to help out with adding new features!

* flair
* proper messaging


License
------------
All of the code contained here is licensed by the GNU GPLv3.
