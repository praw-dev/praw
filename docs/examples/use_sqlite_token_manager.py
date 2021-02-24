#!/usr/bin/env python3
"""This example demonstrates using the sqlite token manager for refresh tokens.

In order to run this program, you will first need to obtain one or more valid refresh
tokens. You can use the ``obtain_refresh_token.py`` example to help.

In this example, refresh tokens will be saved into a file ``tokens.sqlite3`` relative to
your current working directory. If your current working directory is under version
control it is strongly encouraged you add ``tokens.sqlite3`` to the version control ignore
list.

This example differs primarily from ``use_file_token_manager.py`` due to the fact that a
shared SQLite3 database can manage many ``refresh_tokens``. While each instance of
Reddit still needs to have 1-to-1 mapping to a token manager, multiple Reddit instances
can concurrently share access to the same SQLite3 database; the same cannot be done with
the FileTokenManager.

Usage:

    EXPORT praw_client_id=<REDDIT_CLIENT_ID>
    EXPORT praw_client_secret=<REDDIT_CLIENT_SECRET>
    python3 use_sqlite_token_manager.py TOKEN_KEY

"""
import os
import sys

import praw
from praw.util.token_manager import SQLiteTokenManager

DATABASE_PATH = "tokens.sqlite3"


def main():
    if "praw_client_id" not in os.environ:
        sys.stderr.write("Environment variable ``praw_client_id`` must be defined\n")
        return 1
    if "praw_client_secret" not in os.environ:
        sys.stderr.write(
            "Environment variable ``praw_client_secret`` must be defined\n"
        )
        return 1
    if len(sys.argv) != 2:
        sys.stderr.write(
            "KEY must be provided.\n\nUsage: python3 use_sqlite_token_manager.py TOKEN_KEY\n"
        )
        return 1

    refresh_token_manager = SQLiteTokenManager(DATABASE_PATH, key=sys.argv[1])
    reddit = praw.Reddit(
        token_manager=refresh_token_manager,
        user_agent="sqlite_token_manager/v0 by u/bboe",
    )

    if not refresh_token_manager.is_registered():
        refresh_token = input("Enter initial refresh token: ").strip()
        refresh_token_manager.register(refresh_token)

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
