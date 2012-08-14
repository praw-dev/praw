# reddit oauth 2 demo

This is a simple web site that demonstrates using
[OAuth 2](http://oauth.net/2/) to identify/verify a user's reddit account.

## Setup

First, visit http://reddit.com/prefs/apps and create a new app. The only fields
that are strictly required are the name (arbitrary) and the redirect uri. For
the redirect uri, use: http://localhost:5000/authorize\_callback

After you create the app, click "edit" on it to expand its details. You'll need
the *client ID* (displayed right below the app name) and the *client secret*
to configure praw.

---

Next, download the code and set up its dependencies:

```
git clone https://github.com/logan/praw.git praw-oauth-demo
cd praw-oauth-demo
virtualenv .
bin/python setup.py develop
bin/pip install flask
```

---

Now, configure praw by putting this in `~/.config/praw.ini`:

```
[reddit]
oauth_client_id: <client id>
oauth_client_secret: <client secret>
```

## Running

Start up your local server:

```
bin/python examples/oauth/account_link.py
```

This should start a service running on http://127.0.0.1:5000. Visit that link
and follow the URL to authorize the service to access your reddit account. Click
"Allow" to be redirected back to the local service, which should then be able
to fetch your account details and display them to you.

If you get a 403 error after following the authorization link to reddit, make
sure you have the right client ID and secret in your praw.ini, and make sure
the redirect uri you've configured in the reddit app is correct.

