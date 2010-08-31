More Examples
--------------
1. Get application ideas from /r/SomebodyMakeThis:

        r = reddit.Reddit
        sr = reddit.get_subreddit("somebodymakethis")
        # Adjust limit as desired
        ideas = sr.get_hot(limit=300)
        apps = filter(lambda x: "app" in x.title.lower(), ideas)
