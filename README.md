Introduction
-------------
This is a Python wrapper for Reddit's API, aiming to be as easy to use as possible. Here's a quick peek, getting the first 10 stories from the 'hot' section of the 'opensource' subreddit.

    import reddit
    r=reddit.Reddit()
    stories = r.get_subreddit('opensource').get_hot(limit=10)

13 Short Examples
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

8. Print url's of user's saved links:

        saved = r.get_saved_links()
        for save in saved:
            print save.url

9. Get comments from all reddits:

        r.get_comments(limit=25)

10. Get content newer than a place-holder id:

        subreddit.get_top(limit=-1, place_holder=story_id)

11. Get comments from a given story:

        story.get_comments()

12. Subscribe to a subreddit:

        subreddit.subscribe()

13. Save a submission:

        submission.save()

14. Create a subreddit:

        s = Subreddit("MyIncredibleSubreddit", r)
        s.create(title="My Incredibly Cool Subreddit", description="It's just incredible.")

15. Friend a user:

        r.friend("ketralnis")

Other (more involved) examples can be found [here](http://www.github.com/mellort/reddit_api/blob/master/EXAMPLES.md).

Features
-------------
Completed:

* login
* save
* subscribe
* voting
* get hot, top, controversial, overview, submitted
* get all comments
* commenting/replying
* caching results

Not Included (yet):

* friending
* register
* submitting
* everything else

Example Applications
--------------------
I coded a few quick applications/scripts with this wrapper:

* A [comment tracker](http://github.com/mellort/reddit_comment_tracker/blob/master/comment_tracker.py), which repeatedly looks at new Reddit comments and can take an action if they meet a specified condition. The example use I gave is replying with an automated message if the body of a comment contains a certain word. (Novelty accounts, anyone?)
* An [account cloner](http://github.com/mellort/reddit_account_cloner/blob/master/account_cloner.py). Given two logins and passwords, it will transfer all of the saved links and subscribed subreddits from the first account to the second.

I hope that this wrapper allows for many more quick and useful applications to be made!

Questions
------------

> How come you don't have caching?

EDIT: I do now :)

> Why is everything so slow?

I tried to be nice to Reddit's servers by sleeping between requests.

> Why don't you have feature X coded yet?

I had a bit of a hard time decyphering the Reddit API. I will hopefully put more time into it soon.

> When I try to look at stories/comments I get a weird UnicodeEncodeError. What gives?

Sometimes there are unicode characters in story titles and in comments. Python versions before 3.0 will have errors printing them. Try something like

    map(unicode, stories)

for a quick view.
