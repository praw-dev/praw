Introduction
-------------
This is a Python wrapper for Reddit's API, aiming to be as easy to use as possible. Here's a peak, getting the first 10 stories from the 'hot' section of the 'opensource' subreddit.

    import reddit
    r=reddit.Reddit()
    stories = r.get_subreddit('opensource').get_hot(limit=10)

12 Short Examples
---------------

1. Logging in:

        r.login(user="username", password="password")

2. Get stories:

        stories = subreddit.get_top(limit=10)

3. Voting:

        story.upvote()
        story.downvote()
        story.vote(direction=0)

4. Get user karma:

        user = r.get_redditor("username")
        print (user.link_karma, user.comment_karma)

5. Comment on story (after login):

        story.comment("text")

6. Reply to comment:

        comment.reply("test")

7. Get user's saved links:

        r.get_saved_links()

8. Get comments from all reddits:

        r.get_comments(limit=25)

9. Get content newer than a place-holder id:

        subreddit.get_top(limit=-1, place_holder=story_id)

10. Get comments from a given story:

        story.get_comments()

11. Subscribe to a subreddit:

        subreddit.subscribe()

12. Save a submission:

        submission.save()

Features
-------------
Completed:

* login
* save
* subscribe
* voting
* get hot, top, controversial
* get all comments
* commenting/replying

Not Included (yet):

* friending
* register
* submitting
* everything else
* caching results

Example Applications
--------------------
I coded a few quick applications/scripts with this wrapper:

* A [comment tracker](http://github.com/mellort/reddit_comment_tracker/blob/master/comment_tracker.py), which repeatedly looks at new Reddit comments and can take an action if they meet a specified condition. The example use I gave is replying with an automated message if the body of a comment contains a certain word. (Novelty accounts, anyone?)
* An [account cloner](http://github.com/mellort/reddit_account_cloner/blob/master/account_cloner.py). Given two logins and passwords, it will transfer all of the saved links and subscribed subreddits from the first account to the second.

I hope that this wrapper allows for many more quick and useful applications to be made!

Questions
------------

> How come you don't have caching?

I couldn't find caching model that didn't require a server and worked with keyword arguments. Care to recommend one?

> Why is everything so slow?

I tried to be nice to Reddit's servers by sleeping between requests.

> Why don't you have feature X coded yet?

I had a bit of a hard time decyphering the Reddit API. I will hopefully put more time into it soon.

> When I try to look at stories/comments I get a weird UnicodeEncodeError. What gives?

Sometimes there are unicode characters in story titles and in comments. Python versions before 3.0 will have errors printing them. Try something like

    map(unicode, stories)

for a quick view.
