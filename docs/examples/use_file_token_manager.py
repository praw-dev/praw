#!/usr/bin/env python3
"""This example demonstrates using the file token manager for refresh tokens.

In order to run this program, you will first need to obtain a valid refresh token. You
can use the `obtain_refresh_token.py` example to help.

In this example, refresh tokens will be saved into a file `refresh_token.txt` relative
to your current working directory. If your current working directory is under version
control it is strongly encouraged you add `refresh_token.txt` to the version control
ignore list.

Usage:

    EXPORT praw_client_id=<REDDIT_CLIENT_ID>
    EXPORT praw_client_secret=<REDDIT_CLIENT_SECRET>
    python3 use_file_token_manager.py

"""
import os
import sys

import praw
from praw.util.token_manager import FileTokenManager

REFRESH_TOKEN_FILENAME = "refresh_token.txt"


def initialize_refresh_token_file():
    if os.path.isfile(REFRESH_TOKEN_FILENAME):
        return

    refresh_token = input("Initial refresh token value: ")
    with open(REFRESH_TOKEN_FILENAME, "w") as fp:
        fp.write(refresh_token)


def main():
    if "praw_client_id" not in os.environ:
        sys.stderr.write("Environment variable ``praw_client_id`` must be defined\n")
        return 1
    if "praw_client_secret" not in os.environ:
        sys.stderr.write(
            "Environment variable ``praw_client_secret`` must be defined\n"
        )
        return 1

    initialize_refresh_token_file()

    refresh_token_manager = FileTokenManager(REFRESH_TOKEN_FILENAME)
    reddit = praw.Reddit(
        token_manager=refresh_token_manager,
        user_agent="use_file_token_manager/v0 by u/bboe",
    )

    scopes = reddit.auth.scopes()
    if scopes == {"*"}:
        print(f"{reddit.user.me()} is authenticated with all scopes")
    elif "identity" in scopes:
        print(
            f"{reddit.user.me()} is authenticated with the following scopes: {scopes}"
        )
    else:
        print(f"You are authenticated with the following scopes: {scopes}")


if __name__ == "__main__":
    sys.exit(main())
