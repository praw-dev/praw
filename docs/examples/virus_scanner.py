import praw
from praw.models.util import stream_generator

reddit = praw.Reddit(
    user_agent="VIRUS CASE SCANNER (by /u/USERNAME)",
    client_id="CLIENT_ID",
    client_secret="CLIENT_SECRET",
    username="USERNAME",
    password="PASSWORD",
)

virus_subreddit = reddit.subreddit("China_Flu")
query = 'canada flair:"New case"'

result_stream = stream_generator(
    virus_subreddit.search, query=query, sort="new"
)

for result in result_stream:
    title = result.title
    link = result.permalink
    print(
        "<Virus Scanner>: New submission found: "
        "https://www.reddit.com{link}".format(link=link)
    )
    print("Submission title: {title}".format(title=title))
