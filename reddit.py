import urllib
import urllib2
import cookielib
import re
import time
try:
    import json
except ImportError:
    import simplejson as json

from memoize import Memoize

DEFAULT_CONTENT_LIMIT = 25

# Some Reddit urls to keep track of
REDDIT_URL = "http://www.reddit.com"
API_URL = REDDIT_URL + "/api"
REDDITOR_PAGE = REDDIT_URL + "/user/%s"
REDDITOR_ABOUT_PAGE = REDDITOR_PAGE + "/about"

# How long to wait between api requests (in seconds)
REDDIT_API_WAIT_TIME = 1
# How long to cache results (in seconds)
CACHE_TIME = 30
memoize = Memoize(timeout=CACHE_TIME)

# For printing with repr or str or unicode, truncate strings to 80 chars
CHAR_LIMIT = 80


class APIException(Exception):
    """Base exception class for these API bindings."""
    pass

class BadCaptcha(APIException):
    """An exception for when an incorrect captcha error is returned."""
    def __str__(self):
        return "Incorrect captcha entered."

class NotLoggedInException(APIException):
    """An exception for when a Reddit user isn't logged in."""
    def __str__(self):
        return "You need to login to do that!"

class InvalidUserPass(APIException):
    """An exception for failed logins."""
    def __str__(self):
        return "Invalid username/password."

def require_login(func):
    """A decorator to ensure that a user has logged in before calling the
    function."""
    def login_reqd_func(self, *args, **kwargs):
        try:
            user = self.user
        except AttributeError:
            user = self.reddit_session.user

        if not user:
            raise NotLoggedInException()
        else:
            return func(self, *args, **kwargs)
    return login_reqd_func

def limit_chars(num_chars=CHAR_LIMIT):
    """A decorator to limit the number of chars in a function that outputs a
    string."""
    def func_limiter(func):
        def func_wrapper(*args, **kwargs):
            value = func(*args, **kwargs)
            if len(value) > num_chars:
                value = value[:num_chars] + "..."
            return value
        return func_wrapper
    return func_limiter

class sleep_after(object):
    """A decorator to add to API functions that shouldn't be called too
    rapidly, in order to be nice to the reddit server.

    Every function wrapped with this decorator will use a collective
    last_call_time attribute, so that collectively any one of the funcs won't
    be callable within REDDIT_API_WAIT_TIME; they'll automatically be delayed
    until the proper duration is reached."""
    last_call_time = 0     # start with 0 to always allow the 1st call

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        call_time = time.time()

        since_last_call = call_time - self.last_call_time
        if since_last_call < REDDIT_API_WAIT_TIME:
            time.sleep(REDDIT_API_WAIT_TIME - since_last_call)

        self.__class__.last_call_time = call_time
        return self.func(*args, **kwargs)

def api_response(func):
    """Decorator to look at the Reddit API response to an API POST request like
    vote, subscribe, login, etc. Basically, it just looks for certain errors in
    the return string. If it doesn't find one, then it just returns True.
    """
    # TODO: add a 'submitting' too quickly error
    def error_checked_func(*args, **kwargs):
        return_value = func(*args, **kwargs)
        if return_value == '{}' or '".error.' not in return_value:
            return True
        elif ".error.USER_REQUIRED" in return_value:
            raise NotLoggedInException()
        elif ".error.WRONG_PASSWORD" in return_value:
            raise InvalidUserPass()
        else:
            raise APIException(return_value)
    return error_checked_func

class RedditObject(object):
    """
    Base class for all Reddit API objects.
    """
    _content_type = None

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self)

    def __str__(self):
        raise NotImplementedError()

    @property
    def content_id(self):
        return "_".join((self._content_type, self.id))

class Voteable(object):
    """
    Additional interface for Reddit objects that can be voted on (currently
    Submission and Comment).
    """
    def vote(self, direction=0):
        """Cast a vote."""
        return self.reddit_session._vote(self.name, direction=direction,
                                         subreddit_name=self.subreddit)

    def upvote(self):
        return self.vote(direction=1)

    def downvote(self):
        return self.vote(direction=-1)

def _modify_relationship(relationship):
    """Modify the relationship between the current user and a target thing.
    Used to support friending (user-to-user), as well as moderating,
    contributor creating, and banning (user-to-subreddit)."""
    url = "http://www.reddit.com/api/friend"

    @require_login
    @api_response
    def do_relationship(self, thing):
        params = {'name': thing,
                  'container': self.user.content_id,
                  'type': relationship,
                  'uh': self.modhash}
        return self._get_page(url, params)
    return do_relationship

class Reddit(RedditObject):
    """A class for a reddit session."""
    DEFAULT_HEADERS = {'User-agent': 'mellorts Python Wrapper for Reddit API'}

    ban = _modify_relationship("banned")
    friend = _modify_relationship("friend")
    make_contributor = _modify_relationship("contributor")
    make_moderator = _modify_relationship("moderator")

    def __init__(self):
        # Set cookies
        self._cookie_jar = cookielib.CookieJar()
        opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self._cookie_jar))
        urllib2.install_opener(opener)

        self.user = None

    def __str__(self):
        return "Open Session (%s)" % (self.user or "Unauthenticated")

    @memoize
    @sleep_after
    def _get_page(self, page_url, params=None, url_data=None):
        """Given a page url and a dict of params, opens and returns the page.

        :param page_url: the url to grab content from.
        :param params: the extra url data to submit
        :param url_data: the GET data to put in the url
        :returns: the open page
        """
        if url_data:
            page_url += "?" + urllib.urlencode(url_data)

        # urllib2.Request throws a 404 for some reason with data=""
        encoded_params = None
        if params:
            encoded_params = urllib.urlencode(params)

        request = urllib2.Request(page_url,
                                  data=encoded_params,
                                  headers=self.DEFAULT_HEADERS)
        response = urllib2.urlopen(request)
        return response.read()

    def _get_json_page(self, page_url, *args, **kwargs):
        """Gets the JSON processed from a page. Takes the same parameters as
        the _get_page method.

        :returns: JSON processed page
        """
        if not page_url.endswith(".json"):
            page_url += ".json"
        response = self._get_page(page_url, *args, **kwargs)
        return json.loads(response)

    def _get_content(self, page_url, limit=DEFAULT_CONTENT_LIMIT,
                    url_data=None, place_holder=None):
        """A method to return Reddit content from a URL. Starts at the initial
        page_url, and fetches content using the `after` JSON data until `limit`
        entries have been fetched, or the `place_holder` has been reached.

        :param page_url: the url to start fetching content from
        :param limit: the maximum number of content entries to fetch. if -1,
            then fetch unlimited entries--this would be used in conjunction with
            the place_holder param.
        :param url_data: extra GET data to put in the url
        :param place_holder: if not None, the method will fetch `limit`
            content, stopping if it finds content with `id` equal to
            `place_holder`.
        :type place_holder: a string corresponding to a Reddit content id, e.g.
            't3_asdfasdf'
        :returns: a list of Reddit content, of type Subreddit, Comment, or
            Submission
        """
        if not url_data:
            url_data = {}

        # A list which we will populate to return with content
        all_content = []
        # Set the after variable initially to none. This variable will keep
        # track of the next page to fetch.
        after = None

        # While we still need to fetch more content to reach our limit, do so.
        while len(all_content) < limit or limit == -1:
            # If the after variable isn't None, add it do the URL of the page
            # we are going to fetch.
            if after:
                url_data["after"] = after
            page_data = self._get_json_page(page_url, url_data=url_data)

            # if for some reason we didn't get data, then break
            if not page_data.get('data'):
                break

            # Get the data from the JSON dict
            data = page_data.get('data')
            children = data.get('children')

            # Keep track of whether or not we've found the place_holder.
            found_place_holder=False

            # Go through each child and convert it to it's appropriate class
            # before adding it to the all_content list. If the child's id
            # matches the place_holder, then note this.
            for child in children:
                # Check the place holder.
                if place_holder and \
                   child.get('data').get('name') == place_holder:
                    found_place_holder=True
                    break

                # Now we create the class instance based on the 'kind' attr
                content_type = child.get('kind')
                content = None

                if content_type == "t3":
                    content = Submission(child.get('data'), self)
                elif content_type == "t1":
                    content = Comment(child.get('data'), self)
                elif content_type == "t5":
                    content = Subreddit(child.get('data') \
                                        .get('display_name'), self)

                all_content.append(content)

            after = data.get('after')

            # If we don't have another listing to get, then break.
            if not after:
                break

            # If we found the place_holder, break
            if found_place_holder is True:
                break

        # Limit the all_content list to the number of entries we want,
        # given by `limit`.
        if limit != -1:
            all_content = all_content[:limit]

        return all_content

    @require_login
    def _fetch_modhash(self):
        """Grab the current user's modhash. Basically, just fetch any Reddit
        HTML page (can just get first 1200 chars) and search for
        'modhash: 1233asdfawefasdf', using re.search to grab the modhash.
        """
        # A small site to fetch the modhash
        URL = REDDIT_URL + "/help"
        # TODO: Should only need ~1200 chars to get the modhash
        data = self._get_page(URL)
        match = re.search(r"modhash[^,]*", data)
        self.modhash = match.group(0).split(": ")[1].strip(" '")

    def get_redditor(self, user_name):
        """Return a Redditor class for the user_name specified."""
        return Redditor(user_name, self)

    def get_subreddit(self, subreddit_name):
        """Returns a Subreddit class for the user_name specified."""
        return Subreddit(subreddit_name, self)

    @api_response
    def login(self, user=None, password=None):
        """Login to Reddit. If no user or password is provided, the user will
        be prompted with raw_input and getpass.getpass.
        """
        URL = API_URL + "/login"

        # Prompt user for necessary fields.
        if not user:
            user = raw_input("Username: ")
        if not password:
            import getpass
            password = getpass.getpass("Password: ")

        self.user = Redditor(user, self)

        # The parameters we need to login.
        params = {'id' : '#login_login-main',
                  'op' : 'login-main',
                  'passwd' : password,
                  'user' : user}
        data = self._get_page(URL, params)

        # Get and store the modhash; it will be needed for API requests
        # which involve this user.
        self._fetch_modhash()

        return data

    @require_login
    @api_response
    def _vote(self, content_id, direction=0, subreddit_name=""):
        """If logged in, vote for the given content_id in the direction
        specified."""
        URL = API_URL + "/vote"

        params = {'id' : content_id,
                  'dir' : direction,
                  'r' : subreddit_name,
                  'uh' : self.modhash}
        return self._get_page(URL, params)

    @require_login
    @api_response
    def _save(self, content_id, unsave=False):
        """If logged in, save the content specified by `content_id`."""
        URL = API_URL + "/save"
        UNSAVE_URL = API_URL + "/unsave"

        executed = 'saved'
        if unsave:
            URL = UNSAVE_URL
            executed = 'unsaved'
        params = {'id': content_id,
                  'executed': executed,
                  'uh': self.modhash}
        return self._get_page(URL, params)

    @require_login
    @api_response
    def _subscribe(self, subreddit_id, unsubscribe=False):
        """If logged in, subscribe to the specified subreddit_id."""
        URL = API_URL + "/subscribe"

        action = 'sub'
        if unsubscribe:
            action = 'unsub'
        params = {'sr': subreddit_id,
                  'action': action,
                  'uh': self.modhash}
        return self._get_page(URL, params)

    @require_login
    def get_my_reddits(self, limit=DEFAULT_CONTENT_LIMIT):
        """Return all of the current user's subreddits."""
        URL = REDDIT_URL + "/reddits/mine"
        reddits = self._get_content(URL, limit=limit)
        return reddits

    @api_response
    def _comment(self, content_id, subreddit_name=None, text=""):
        """Comment on the given content_id with the given text."""
        URL = API_URL + "/comment"
        params = {'thing_id': content_id,
                  'text': text,
                  'uh': self.modhash,
                  'r': subreddit_name}
        return self._get_page(URL, params)

    def get_homepage(self):
        """Return a subreddit-style class of the reddit homepage."""
        return RedditPage(REDDIT_URL, "reddit.com", self)

    @require_login
    def get_saved_links(self, limit=-1):
        """Return a listing of the logged-in user's saved links."""
        URL = REDDIT_URL + "/saved"
        return self._get_content(URL, limit=limit)

    def get_comments(self, limit=DEFAULT_CONTENT_LIMIT,
                     place_holder=None):
        """Returns a listing from reddit.com/comments"""
        URL = REDDIT_URL + "/comments"
        return self._get_content(URL, limit=limit, place_holder=place_holder)

    def _get_submission_comments(self, submission_url):
        json_data = self._get_json_page(submission_url)
        main_content = json_data[0] # this isn't used
        json_comments = json_data[1]['data']['children']

        comments = map(self._json_data_to_comment, json_comments)
        return comments

    def _json_data_to_comment(self, json_dict):
        data = json_dict['data']
        replies = data.pop('replies', None)

        root_comment = Comment(data, self)

        if replies:
            children = replies['data']['children']

            converted_children = map(self._json_data_to_comment, children)
            root_comment.replies = converted_children
        return root_comment

def _get_section(subpath=""):
    def closure(self, sort="new", time="all", limit=DEFAULT_CONTENT_LIMIT,
                place_holder=None):
        url_data = {"sort" : sort, "time" : time}
        return self.reddit_session._get_content(self.URL + subpath,
                                                limit=int(limit),
                                                url_data=url_data,
                                                place_holder=place_holder)
    return closure

class Redditor(RedditObject):
    """A class for Redditor methods."""

    _content_type = "t2"
    # Redditor fields exposed by the API:
    _api_fields = ['comment_karma', 'created', 'created_utc', 'has_mail',
                   'has_mod_mail', 'id', 'is_mod', 'link_karma', 'name']
    get_overview = _get_section("/")
    get_comments = _get_section("/comments")
    get_submitted = _get_section("/submitted")

    def __init__(self, user_name, reddit_session):
        self.user_name = user_name
        # Store the urls we will need internally
        self.URL = REDDITOR_PAGE % self.user_name
        self.ABOUT_URL = REDDITOR_ABOUT_PAGE % self.user_name
        self.reddit_session = reddit_session

    @limit_chars()
    def __str__(self):
        """Have the str just be the user's name"""
        return self.user_name

    def __getattr__(self, attr):
        if attr in self._api_fields:
            data = self.reddit_session._get_json_page(self.ABOUT_URL)
            return data['data'].get(attr)
        raise AttributeError("'%s' object has no attribute '%s'" % (
                                            self.__class__.__name__, attr))

    def _get_captcha(self):
        """
        Get a new captcha (to be viewed and submitted).
        """
        URL = API_URL + "/new_captcha"
        VIEW_URL = REDDIT_URL + "/captcha"
        return self.reddit_session._get_json_page(URL, {})

    def register(self, passwd, captcha):
        """
        Register a new user.
        """
        URL = API_URL + "/register"
        params = {"captcha" : captcha,
                  "op" : "reg",
                  "passwd" : passwd,
                  "passwd2" : passwd,
                  "user" : self.user_name}
        return self.reddit_session._get_json_page(URL, params)

    create = register # just an alias to provide a somewhat uniform API

def _get_sorter(subpath="", **defaults):
    def closure(self, limit=DEFAULT_CONTENT_LIMIT, place_holder=None, **data):
        for k, v in defaults.items():
            if k == "time":
                # time should be "t" in the API data dict
                k = "t"
            data.setdefault(k, v)
        return self.reddit_session._get_content(self.URL + subpath,
                                                limit=int(limit),
                                                url_data=data,
                                                place_holder=place_holder)
    return closure

class RedditPage(RedditObject):
    """A class for Reddit pages, essentially reddit listings. This is separated
    from the subreddits because reddit.com isn't exactly a subreddit."""

    _content_type = "t5"
    get_hot = _get_sorter("/")
    get_controversial = _get_sorter("/controversial", time="day")
    get_new = _get_sorter("/new", sort="rising")
    get_top = _get_sorter("/top", time="day")

    def __init__(self, url, name, reddit_session):
        self.URL = url
        self.display_name = name
        self.reddit_session = reddit_session

    @limit_chars()
    def __str__(self):
        """Just display the reddit page name."""
        return self.display_name

class Subreddit(RedditPage):
    """A class for Subreddits. This is a subclass of RedditPage."""

    # Subreddit fields exposed by the API:
    _api_fields = ['display_name', 'name', 'title', 'url', 'created',
                   'created_utc', 'over18', 'subscribers', 'id', 'description']
    _sections = ['hot', 'new', 'controversial', 'top']

    def __init__(self, subreddit_name, reddit_session):
        super(Subreddit, self).__init__(REDDIT_URL + "/r/" + subreddit_name,
                                        subreddit_name,
                                        reddit_session)
        self.ABOUT_URL = self.URL + "/about"

    def __str__(self):
        return self.display_name

    def __getattr__(self, attr):
        if attr in self._api_fields:
            data = self.reddit_session._get_json_page(self.ABOUT_URL)
            return data['data'].get(attr)
        raise AttributeError("'%s' object has no attribute '%s'" % (
                                            self.__class__.__name__, attr))

    @require_login
    def create(self, title, description="", language="English [en]",
               type="public", content_options="any", other_options=None,
               domain=""):
        """
        Create a new subreddit.
        """
        # TODO: Implement the rest of the options.
        URL = API_URL + "/site_admin"
        params = {"name" : self.display_name,
                  "title" : title,
                  "type" : type,
                  "uh" : self.reddit_session.modhash}
        return self.reddit_session._get_page(URL, params)

    def subscribe(self):
        """If logged in, subscribe to the given subreddit."""
        return self.reddit_session._subscribe(self.name)

    def unsubscribe(self):
        """If logged in, unsubscribe from the given subreddit."""
        return self.reddit_session._subscribe(self.name,
                                              unsubscribe=True)

class Submission(RedditObject, Voteable):
    """A class for submissions to Reddit."""

    _content_type = "t3"

    def __init__(self, json_dict, reddit_session):
        self.__dict__.update(json_dict)
        self.reddit_session = reddit_session

    @limit_chars()
    def __str__(self):
        return (str(self.score) + " :: " + self.title)

    def get_comments(self):
        comments_url = REDDIT_URL + self.permalink
        comments = self.reddit_session._get_submission_comments(comments_url)
        return comments

    def save(self):
        return self.reddit_session._save(self.name)

    def unsave(self):
        return self.reddit_session._save(self.name, unsave=True)

    def comment(self, text):
        """If logged in, comment on the submission using the specified text."""
        return self.reddit_session._comment(self.name,
                                            subreddit_name=self.subreddit,
                                            text=text)

class Comment(RedditObject, Voteable):
    """A class for comments."""

    _content_type = "t1"

    def __init__(self, json_dict, reddit_session):
        self.__dict__.update(json_dict)
        self.reddit_session = reddit_session
        self.replies = []

    @limit_chars()
    def __str__(self):
        if self.__dict__.get('body'):
            return self.body
        else:
            return "[[need to fetch more comments]]"

    def reply(self, text):
        """Reply to the comment with the specified text."""
        return self.reddit_session.comment(self.name,
                                           subreddit_name=self.subreddit,
                                           text=text)
