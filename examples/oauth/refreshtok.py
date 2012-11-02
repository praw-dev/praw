import functools
import hashlib
import json
import mimetools
import random
import sys
import threading
import time
import traceback
import urllib2
import uuid

import flask
from flask import request
import praw
import rauth.service

#SITE = "local-oauth"
SITE = "reddit"
TEST_SUBREDDIT = "intortus"

# Generate a unique value to pass to and from oauth.reddit.com as session state.
# This serves as a CSRF countermeasure, but this implementation isn't
# particularly secure, just a proof of concept.
oauth_state = hashlib.sha1(str(uuid.uuid1())).hexdigest()

heartbeat_thread = None

def get_authorize_url():
    """Constructs oauth.reddit.com URL to send user to for authorization."""
    client = praw.Reddit(__name__, site_name=SITE)
    return client.get_authorize_url(
        redirect_uri=flask.url_for("authorize_callback", _external=True),
        scope="%s:identity" % TEST_SUBREDDIT, state=oauth_state,
        refreshable=True)

def retry_on_401(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except urllib2.HTTPError, ex:
            if ex.code == 401:
                print 'got a 401, refreshing'
                self.client.refresh_access_token(self.redirect_uri)
                return f(self, *args, **kwargs)
    return wrapper

class HeartbeatThread(threading.Thread):
    def __init__(self, authorized_client):
        self.client = authorized_client
        self.redirect_uri = flask.url_for("authorize_callback", _external=True)
        threading.Thread.__init__(self)

    def run(self):
        while True:
            self.heartbeat()
            time.sleep(60)

    @retry_on_401
    def heartbeat(self):
        #post = self.client.submit(TEST_SUBREDDIT, time.ctime(), text='...')
        #print 'Posted %r' % post
        response = self.client.request_json(
            praw.urljoin(self.client.config._oauth_url, "api/v1/me"))
        print 'Got identity data: %r' % response
        

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
            return flask.Response(flask.stream_with_context(run()))
        return wrapped
    return page_decorator

app = flask.Flask("oauth-testall")

@page("/")
def home():
    if heartbeat_thread:
        yield '<p>heartbeat already running</p>'
    else:
         yield '<a href="%s">click here to authorize</a>' % get_authorize_url()

@page("/authorize_callback")
def authorize_callback():
    global heartbeat_thread

    if heartbeat_thread:
        yield '<p>Error: heartbeat already running</p>'

    if "error" in request.args:
        yield '<p>Error: %s</p>' % request.args.get("error")
        return

    if request.args.get("state") != oauth_state:
        yield '<p>State mismatch! Possible CSRF detected.</p>'
        return

    yield '<p>Thank you for authorizing. Fetching access token...</p>'

    code = request.args.get("code")
    client = praw.Reddit(__name__, site_name=SITE)
    client.config.oauth.session.verify = False
    client.get_access_token(
        code, flask.url_for("authorize_callback", _external=True),
        refreshable=True)

    heartbeat_thread = HeartbeatThread(client)
    heartbeat_thread.start()

    yield '<p>Access token retrieved. Heartbeat started</p>'


if __name__ == "__main__":
    app.run(debug=True) #, ssl_context="adhoc")
