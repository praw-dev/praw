Python Wrapper for Reddit's API
===============================
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
    -login
    -save
    -subscribe
    -voting
    -get hot, top, controversial
    -get all comments
    -commenting/replying
Not Included (yet):
    -friending
    -register
    -submitting
    -everything else









