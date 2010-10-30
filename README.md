Introduction
------------

This is a Python wrapper for Reddit's API, aiming to be as easy to use as possible. Here's a quick peek, getting the first 10 stories from the 'hot' section of the 'opensource' subreddit.

    import reddit_api as reddit
    r = reddit.Reddit()
    stories = r.get_subreddit('opensource').get_hot(limit=10)

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

        s = r.get_subreddit("MyIncredibleSubreddit")
        s.create(title="My Incredibly Cool Subreddit", description="It's just incredible.")

16. Friend a user:

        r.friend("ketralnis")

Other (more involved) examples can be found [here](http://www.github.com/mellort/reddit_api/blob/master/EXAMPLES.md).

Features (Outdated list, to be updated soon)
-------------

Completed:

* login
* save
* delete
* subscribe
* voting
* get hot, top, controversial, overview, submitted
* get all comments
* commenting/replying
* caching results
* friending/moderating/contributing/banning

Example Applications
--------------------

I coded a few quick applications/scripts with this wrapper:

* A [comment tracker](http://github.com/mellort/reddit_comment_tracker/blob/master/comment_tracker.py), which repeatedly looks at new Reddit comments and can take an action if they meet a specified condition. The example use I gave is replying with an automated message if the body of a comment contains a certain word. (Novelty accounts, anyone?)
* An [account cloner](http://github.com/mellort/reddit_account_cloner/blob/master/account_cloner.py). Given two logins and passwords, it will transfer all of the saved links and subscribed subreddits from the first account to the second.

I hope that this wrapper allows for many more quick and useful applications to be made!

Questions
------------

> Why is everything so slow?

Usually that has to do with how fast reddit is responding at the moment. Check the site, see if it's responding quicker when accessing it in your browser. Otherwise, we respect the "no more than one API call per second" rule, so if you're trying to do a bunch of quick requests in succession you're going to be spaced out to one call per second. If you're having a specific issue besides something covered by one of those two things, please let us know (or file a ticket) and we'll check it out.

> Why don't you have feature X coded yet?

If feature X is commenting / submitting / PMing, it's because it's not really gonna happen considering how easily it'd be to misuse (even though it's easy enough without these bindings). Otherwise, it's because we didn't need it :). We tried to add everything we imagined would be useful to anyone, but if there's something missing that you'd like, please let us know what you're looking for and we can add it!
