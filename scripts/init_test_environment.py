#!/usr/bin/env python
import praw
import sys


PASSWORD = '1111'
SUBMISSIONS = ({'subreddit': 'reddit_api_test', 'text': 'blah blah blah',
                'title': 'Init Submission', 'username': 'pyapitestuser3'},
               {'subreddit': 'python', 'title': 'Python Website',
                'url': 'http://python.org', 'username': 'subreddit_stats'})
USER_TO_SUBS = {'PyAPITestUser2': ('reddit_api_test', 'reddit_api_test2'),
                'PyAPITestUser3': ('Python',),
                'PyAPITestUser4': (),
                'PyAPITestUser5': (),
                'PyAPITestUser6': ()}


def create_redditors(r):
    for username in USER_TO_SUBS:
        try:
            r.create_redditor(username, PASSWORD)
            print('Created user: {0}'.format(username))
        except praw.errors.UsernameExists:
            pass


def create_subreddits(r):
    for username, subreddit_names in USER_TO_SUBS.items():
        if not subreddit_names:
            continue
        r.login(username, PASSWORD)
        for name in subreddit_names:
            try:
                r.create_subreddit(name, name)
                print('Created subreddit: {0}'.format(name))
            except praw.errors.SubredditExists:
                pass


def make_submissions(r):
    for sub_info in SUBMISSIONS:
        r.login(sub_info['username'], PASSWORD)
        del sub_info['username']
        try:
            r.submit(**sub_info)
            print('Make submission: {0}'.format(sub_info['title']))
        except praw.errors.AlreadySubmitted:
            pass


def adjust_subscriptions(r):
    """Subscribe users only to the test subreddits."""
    subreddits = set()
    for subs in USER_TO_SUBS.values():
        subreddits.update(x.lower() for x in subs)

    for username in USER_TO_SUBS:
        r.login(username, PASSWORD)
        subscribed = set(x.display_name.lower()
                         for x in r.user.my_reddits(limit=None))
        for subreddit_name in subscribed - subreddits:
            r.unsubscribe(subreddit_name)
            print('{0} unsubscribed from {1}'.format(username, subreddit_name))
        for subreddit_name in subreddits - subscribed:
            r.subscribe(subreddit_name)
            print('{0} subscribed to {1}'.format(username, subreddit_name))


def main():
    r = praw.Reddit('praw test init', 'local')
    #create_redditors(r)
    #create_subreddits(r)
    #make_submissions(r)
    adjust_subscriptions(r)


    print('If this is the first time you are running this script, you may want'
          ' to update the default subreddits on your local instance.')
    print('To do that run: sudo /sbin/start --quiet reddit-job-update_reddits')
    return

    # Add a comment
    c = s.add_comment('some more text')
    # Spam the comment
    c.remove()
    # add flair to subreddit
    r.set_flair('python', 'pyapitestuser2', 'some flair test', 'flair-class')


if __name__ == '__main__':
    sys.exit(main())
