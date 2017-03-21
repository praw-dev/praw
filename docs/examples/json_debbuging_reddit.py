import json
import os
from prawcore import Requestor
import praw
from praw.const import USER_AGENT_FORMAT


# Change these to your CLIENT_ID and CLIENT_SECRET or add them to env
PRAW_CLIENT_ID = os.environ.get('PRAW_CLIENT_ID')
PRAW_CLIENT_SECRET = os.environ.get('PRAW_CLIENT_SECRET')
USER_AGENT = 'praw_json_debugging_reddit_example'


class JSONDebugRequestor(Requestor):
    def request(self, *args, **kwargs):
        response = super().request(*args, **kwargs)
        print('Response for url:', response.url)
        print(json.dumps(response.json(), indent=4))
        return response


def main():
    user_agent = USER_AGENT_FORMAT.format(USER_AGENT)
    debug_requestor = JSONDebugRequestor(user_agent)
    reddit = praw.Reddit(user_agent=USER_AGENT,
                         client_id=PRAW_CLIENT_ID,
                         client_secret=PRAW_CLIENT_SECRET,
                         requestor=debug_requestor)
    print('Using debug requestor:', reddit._core._requestor is debug_requestor)
    a_comment = reddit.comment('ddisuxh')
    print('\n\nRetrieved comment body: ', a_comment.body)


if __name__ == '__main__':
    main()
