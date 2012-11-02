import functools
import hashlib
import sys
import traceback
import uuid

import flask
from flask import request
import praw
import rauth.service

SITE = "reddit"

# Generate a unique value to pass to and from oauth.reddit.com as session state.
# This serves as a CSRF countermeasure, but this implementation isn't
# particularly secure, just a proof of concept.
oauth_state = hashlib.sha1(str(uuid.uuid1())).hexdigest()

def get_authorize_url():
    """Constructs oauth.reddit.com URL to send user to for authorization."""
    client = praw.Reddit(__name__, site_name=SITE)
    return client.get_authorize_url(
        redirect_uri=flask.url_for("authorize_callback", _external=True),
        scope="identity", state=oauth_state)

def get_access_token(code):
    """Fetches and returns access token from reddit.com."""
    client = praw.Reddit(__name__, site_name=SITE)
    return client.get_access_token(
        code, flask.url_for("authorize_callback", _external=True))

def page(*args, **kwargs):
    def page_decorator(f):
        @app.route(*args, **kwargs)
        @functools.wraps(f)
        def wrapped():
            def run():
                yield '<p><a href="/">home</a></p>'
                try:
                    for item in f():
                        yield item
                except:
                    ex_type, ex, tb = sys.exc_info()
                    yield "<p>Error: %s</p>" % ex
                    yield "<pre>"
                    for line in traceback.format_tb(tb):
                        yield flask.escape(line)
                    yield "</pre>"
                yield '<p><a href="%s">try again</a></p>' % get_authorize_url()
            return flask.Response(flask.stream_with_context(run()))
        return wrapped
    return page_decorator


app = flask.Flask('account-link-demo')

@app.route("/")
def home():
    return ('<a href="%s">authorize here</a> to link your account'
            % get_authorize_url())

@page("/authorize_callback")
def authorize_callback():
    if "error" in request.args:
        yield "<p>Error: %s</p>" % request.args.get("error")
        return
    elif request.args.get("state") != oauth_state:
        yield "<p>State mismatch! Possible CSRF detected.</p>"
        return

    yield "<p>Thank you for authorizing. Fetching access token...</p>"

    code = request.args.get("code")
    token = get_access_token(code)

    yield "<p>Access token retrieved. Fetching user information...</p>"
    client = praw.Reddit(__name__, site_name=SITE, access_token=token)
    response = client.request_json(
        praw.urljoin(client.config._ssl_url, "api/v1/me"))

    yield (
        "Welcome, %(name)s! You have %(link_karma)s link karma and"
        " %(comment_karma)s comment karma.") % response

if __name__ == "__main__":
    app.run(debug=True) #, ssl_context="adhoc")
