#!/usr/bin/env python3
"""This is to generate the awards table."""
import argparse
import random
import socket
import sys
import time
from copy import copy
from datetime import datetime
from json import dumps, load
from os.path import isdir, split
from textwrap import wrap

import requests
import tabulate

from praw import Reddit

AWARD_TYPES = {
    "a": lambda _: True,
    "g": lambda award: award["award"]["awardType"] == "GLOBAL",
    "s": lambda award: award["award"]["awardType"] == "SUBREDDIT",
    "m": lambda award: award["award"]["awardType"] == "MODERATOR",
}


def receive_connection():
    """Wait for and then return a connected socket..

    Opens a TCP connection on port 8080, and waits for a single client.

    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 65010))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client


def send_message(client, message):
    """Send message to client and close the connection."""
    print(message)
    client.send(f"HTTP/1.1 200 OK\r\n\r\n{message}".encode())
    client.close()


def get_request_params(client_id, redirect_uri, thing):
    scopes = ["*"]

    reddit = Reddit(
        client_id=client_id,
        client_secret=None,
        redirect_uri=redirect_uri,
        user_agent="Award fetcher by u/Lil_SpazJoekp",
    )
    state = str(random.randint(0, 65000))
    url = reddit.auth.url(duration="temporary", scopes=scopes, state=state)
    print(f"Open this url in your browser: {url}")
    sys.stdout.flush()

    client = receive_connection()
    data = client.recv(1024).decode("utf-8")
    param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
    params = dict([token.split("=") for token in param_tokens])

    if state != params["state"]:
        send_message(
            client,
            f"State mismatch. Expected: {state} Received: {params['state']}",
        )
        return None
    elif "error" in params:
        send_message(client, params["error"])
        return None

    reddit.auth.authorize(params["code"])
    thing = list(reddit.info(fullnames=[thing]))[0]
    subreddit = thing.subreddit_id
    return reddit._authorized_core._authorizer.access_token, thing.fullname, subreddit


def fetch_awards(client_id, redirect_uri, thing_fullname):
    access_code, thing, subreddit = get_request_params(
        client_id, redirect_uri, thing_fullname
    )
    if access_code:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_code}",
            "User-Agent": "Award fetcher by u/Lil_SpazJoekp",
        }
        params = {"request_timestamp": str(int(time.time() * 1000))}
        data = f'{{"id":"4fb406bbd0cf","variables":{{"subredditId":"{subreddit}","thingId":"{thing}","includeGroup":true}}}}'
        response = requests.post(
            "https://gql.reddit.com/", headers=headers, params=params, data=data
        )
        return response.json()
    return None


def main():
    """Runs the main function.

    usage: generate_award_table.py [-t] [-f] format [-c] client_id [-T] submission or
    comment fullname [-l] load file [-o] out file.

    Grabs the awards available to award a submission or comment.

    :param --type [-t]: One of ``a`` for all, ``g`` for global, ``s`` for subreddit, or
        ``m`` for moderator. Determines the types of awards to give (default: ``g``).
    :param --format [-f]: One of ``j`` for json or ``r`` for rst.
    :param --client_id [-c]: Used to fetch the awards. Must be a 1st party client id.
        Note: If this is passed [redirect_uri] and [thing] must be provided. If not
        [load_file] must be passed.
    :param --redirect_uri [-r]: Redirect uri for the auth flow as this requires an
        access token.
    :param --thing [-T]: A submission or comment fullname.
    :param --load_file [-l]: Load award json from file. This is useful if you grab the
        JSON response from a browser request. Can not be used with [client_id]. If not
        provided [client_id] and [thing] is required.
    :param --out_file [-o]: File to write the formatted. If not provided output will be
        written to STDOUT.

    """
    parser = argparse.ArgumentParser(
        description="Parse awards and generate an rst formatted table"
    )

    parser.add_argument(
        "-t",
        "--type",
        action="store",
        choices=["a", "g", "s", "m"],
        default="g",
        help=(
            "One of 'a' for all, 'g' for global, 's' for subreddit, or 'm' for"
            " moderator. Determines the types of awards to give (default: 'g')."
        ),
    )
    parser.add_argument(
        "-f",
        "--format",
        action="store",
        choices=["j", "r"],
        default="r",
        help="One of 'j' for json or 'r' for rst (default: 'r').",
    )
    parser.add_argument(
        "-c",
        "--client_id",
        action="store",
        default=None,
        help=(
            "Used to fetch the awards. Must be a 1st party client id. Note: If this is"
            " passed [thing] and [subreddit] must be provided."
        ),
    )
    parser.add_argument(
        "-r",
        "--redirect_uri",
        action="store",
        default=None,
        help="Redirect uri for the auth flow as this requires an access token",
    )
    parser.add_argument(
        "-T",
        "--thing",
        action="store",
        default=None,
        help=(
            "A submission or comment fullname. Must be used in conjunction with"
            " [client_id]."
        ),
    )
    parser.add_argument(
        "-l",
        "--load_file",
        action="store",
        default=None,
        help=(
            "Load award json from file. This is useful if you grab the JSON response"
            " from a browser request. Can not be used with [client_id]. If not provided"
            " [client_id] and [thing] is required."
        ),
    )
    parser.add_argument(
        "-o",
        "--out_file",
        action="store",
        default=None,
        help=(
            "File to write the formatted. If not provided output will be written to"
            " STDOUT."
        ),
    )
    args = parser.parse_args()
    award_type = args.type
    output_format = args.format
    client_id = args.client_id
    redirect_uri = args.redirect_uri
    thing = args.thing
    load_file = args.load_file
    out_file = args.out_file

    # check for client id or load file reject if both provided
    if client_id and load_file:
        print("Both 'client_id' and 'load_file' can not be provided")
        return
    if client_id:
        if not thing:
            print("'thing' is requited if 'client_id' is provided")
            return
        award_json = fetch_awards(client_id, redirect_uri, thing)
    else:
        with open(load_file) as f:
            award_json = load(f)
    awards = sorted(
        validate_award_json(award_json, award_type),
        key=lambda d: (
            0 if d["id"].startswith("gid") else 1,
            d["coinPrice"],
            d["name"],
        ),
    )
    if output_format == "j":
        if load_file:
            print(
                "Uh...there's nothing to do if you want output the loaded JSON from"
                " 'load_file' as JSON"
            )
            return
        final_content = dumps(award_json, ident=4)
    else:
        rows = [
            [
                f"{award['name']}",
                f".. image:: {award['icon64']['url']}",
                award["id"],
                "\n".join(wrap(award["description"], width=50)),
                str(award["coinPrice"]),
            ]
            for award in awards
        ]
        table = tabulate.tabulate(
            rows,
            ["Name", "Icon", "Gild Type", "Description", "Cost"],
            tablefmt="rst",
            disable_numparse=True,
        )
        final_content = (
            "This is a list of known global awards (as of "
            f"{datetime.today().strftime('%m/%d/%Y')})\n\n{table}"
        )
    if out_file is None:
        print(final_content)
    else:
        if isdir(split(out_file)[0]):
            with open(out_file, "w") as f:
                f.write(final_content)
            print(f"Successfully written awards to {out_file!r}")
        else:
            print(f"THe directory, {split(out_file)[0]!r}, does not exist.")


def validate_award_json(award_json, award_type):
    awards = copy(award_json)
    for key in ["data", "subredditInfoById", "sortedUsableAwards"]:
        try:
            awards = awards[key]
        except KeyError:
            print("Invalid award JSON")
    return [award["award"] for award in awards if AWARD_TYPES[award_type](award)]


if __name__ == "__main__":
    main()
