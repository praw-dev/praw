#!/usr/bin/env python
import praw
import sys

def main():
    r = praw.Reddit('praw test init', 'local')

    # Create pyapitestuser2
    try:
        r.create_redditor('PyApiTestUser2', '1111')
    except (praw.errors.ExceptionList, praw.errors.APIException):
        pass

    # Create pyapitestuser3
    try:
        r.create_redditor('PyApiTestUser3', '1111')
    except (praw.errors.ExceptionList, praw.errors.APIException):
        pass


    # Login
    r.login('pyapitestuser2', '1111')

    # Create reddit_api_test subreddit
    try:
        r.create_subreddit('reddit_api_test', 'Reddit API Test')
    except (praw.errors.ExceptionList, praw.errors.APIException):
        pass

    # Create reddit_api_test2 subreddit
    try:
        r.create_subreddit('reddit_api_test2', 'Reddit API Test 2')
    except (praw.errors.ExceptionList, praw.errors.APIException):
        pass

    # Create a submission
    s = r.submit('reddit_api_test', 'Init Submission', text='blah blah blah')

    # Add a comment
    c = s.add_comment('some more text')

    # Spam the comment
    c.remove()

    # Create python subreddit as a different user
    r.login('pyapitestuser3', '1111')
    try:
        r.create_subreddit('python', 'python')
    except (praw.errors.ExceptionList, praw.errors.APIException):
        pass

    # add a submission to subreddit
    try:
        r.submit('python', 'Python Website', url='http://python.org')
    except praw.errors.APIException:
        pass

    # add flair to subreddit
    r.set_flair('python', 'pyapitestuser2', 'some flair test', 'flair-class')



if __name__ == '__main__':
    sys.exit(main())
