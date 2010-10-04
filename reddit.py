import urllib
import urllib2
import cookielib
import re
import time
try:
    import json
except ImportError:
    import simplejson as json

from functools import wraps
from urlparse import urljoin

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

class require_captcha(object):
    """
    Decorator for methods that require captchas.
    """
    URL = API_URL + "/new_captcha"
    VIEW_URL = REDDIT_URL + "/captcha"

    def __init__(self, func):
        self.func = func
        self.captcha_id = None
        self.captcha = None

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return self.__class__(self.func.__get__(obj, type))

    def __call__(self, *args, **kwargs):
        # use the captcha passed in if given, otherwise get one
        self.captcha_id, self.captcha = kwargs.get("captcha",
                                                   self.get_captcha())
        result = self.func(*args, **kwargs)
        result.update(self.captcha_as_dict)
        return result

    @property
    def captcha_as_dict(self):
        return {"iden" : self.captcha_id,
                "captcha" : self.captcha}

    @property
    def captcha_url(self):
        if self.captcha_id:
            return self.VIEW_URL + "/" + self.captcha_id + ".png"

    def get_captcha(self):
        data = Reddit()._request_json(self.URL, {"renderstyle" : "html"})
        # TODO: fix this, it kills kittens
        self.captcha_id = data["jquery"][-1][-1][-1]
        print "Captcha URL: " + self.captcha_url
        self.captcha = raw_input("Captcha: ")
        return self.captcha_id, self.captcha

def require_login(func):
    """A decorator to ensure that a user has logged in before calling the
    function."""
    @wraps(func)
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
        @wraps(func)
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

def url(url=None, url_data=None, json=False):
    """
    Decorator to allow easy definitions of functions and methods. Just specify
    the url in a parameter to this decorator, and return the dict containing
    the appropriate parameters for the method.

    If the url needs to be decided within the method (like if the method is
    toggling an action, you can also pass in an empty url to the decorator, and
    then return a tuple (url, params) [This doesn't work yet since nonlocal is
    3.x only].

    For json, set json to True.
    """
    def request(func):
        # @wraps(func)
        def wrapper(self, *args, **kwargs):
            params = func(self, *args, **kwargs)
            # nonlocal url
            # if not url:
            #    url, params = params
            if json:
                requester = self._request_json
            else:
                requester = self._request
            return requester(url, params, url_data)
        return wrapper
    return request

def api_response(func):
    """Decorator to look at the Reddit API response to an API POST request like
    vote, subscribe, login, etc. Basically, it just looks for certain errors in
    the return string. If it doesn't find one, then it just returns True.
    """
    # TODO: add a 'submitting' too quickly error
    @wraps(func)
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

def _get_section(subpath=""):
    """
    Used by the Redditor class to generate each of the sections (overview,
    comments, submitted).
    """
    def closure(self, sort="new", time="all", limit=DEFAULT_CONTENT_LIMIT,
                place_holder=None):
        url_data = {"sort" : sort, "time" : time}
        return self.reddit_session._get_content(self.URL + subpath,
                                                limit=int(limit),
                                                url_data=url_data,
                                                place_holder=place_holder)
    return closure

def _get_sorter(subpath="", **defaults):
    """
    Used by the Reddit Page classes to generate each of the currently supported
    sorts (hot, top, new, best).
    """
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

def _modify_relationship(relationship, unlink=False):
    """
    Modify the relationship between the current user or subreddit and a target
    thing.

    Used to support friending (user-to-user), as well as moderating,
    contributor creating, and banning (user-to-subreddit).
    """
    # the API uses friend and unfriend to manage all of these relationships
    URL = API_URL + "/friend"
    UNFRIEND_URL = API_URL + "/unfriend"

    # unlink: remove the relationship instead of creating it
    if unlink:
        URL = UNFRIEND_URL

    @url(URL)
    @require_login
    def do_relationship(self, thing):
        return {'name': thing,
                'container': self.content_id,
                'type': relationship,
                'uh': self.modhash}
    return do_relationship

class RedditObject(object):
    """
    Base class for all Reddit API objects.
    """
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self)

    def __str__(self):
        raise NotImplementedError()

class RedditContentObject(RedditObject):
    """
    Base class for everything besides the Reddit class.

    Represents actual reddit objects (Comment, Redditor, etc.).
    """
    def __init__(self, reddit_session, name=None, json_dict=None, fetch=True):
        """
        Create a new object either by name or from the dict of attributes
        returned by the API. Creating by name will retrieve the proper dict
        from the API.

        The fetch parameter specifies whether to retrieve the object's
        information from the API (only matters when it isn't provided using
        json_dict).
        """
        if not name and not json_dict:
            # one of these at least is required
            raise TypeError("Either the name or json dict is required!.")

        self.reddit_session = reddit_session

        if not json_dict:
            if fetch:
                json_dict = self._get_json_dict()
            else:
                json_dict = {}
        self.__dict__.update(json_dict)

        # set an attr containing whether we've fetched all the attrs from API
        self._populated = bool(json_dict) or fetch

    def __getattr__(self, attr):
        """
        Instead of special casing to figure out if we're calling requests from
        a reddit content object rather than a Reddit object, we can just allow
        the reddit content objects to lookup the attrs that we choose in their
        attached Reddit session object.
        """
        retrievable_attrs = ("user", "modhash", "_request", "_request_json")
        if attr in retrievable_attrs:
            return getattr(self.reddit_session, attr)
        else:
            # TODO: maybe restrict this again to known API fields
            if not self._populated:
                json_dict = self._get_json_dict()
                self.__dict__.update(json_dict)
                self._populated = True
                return getattr(self, attr)

    def _get_json_dict(self):
        response = self._request_json(self.ABOUT_URL, as_objects=False)
        json_dict = response.get("data")
        return json_dict

    @classmethod
    def from_api_response(cls, reddit_session, json_dict):
        return cls(reddit_session, json_dict=json_dict)

    @property
    def content_id(self):
        """
        Get the content id for this object. Just appends the appropriate
        content type ("t1", "t2", ..., "t5") to this object's id.
        """
        return "_".join((self.kind, self.id))

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

class Reddit(RedditObject):
    """A class for a reddit session."""
    DEFAULT_HEADERS = {'User-agent': 'mellorts Python Wrapper for Reddit API'}

    friend = _modify_relationship("friend")
    friend.__doc__ = "Friend the target user."

    unfriend = _modify_relationship("friend", unlink=True)
    unfriend.__doc__ = "Unfriend the target user."

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
    def _request(self, page_url, params=None, url_data=None):
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
                                  headers=Reddit.DEFAULT_HEADERS)
        response = urllib2.urlopen(request)
        return response.read()

    def _request_json(self, page_url, params=None, url_data=None,
                      as_objects=True):
        """Gets the JSON processed from a page. Takes the same parameters as
        the _request method, plus a param to control whether objects are
        returned.

        :param page_url
        :param params
        :param url_data
        :param as_objects: Whether to return constructed Reddit objects or the
        raw json dict.
        :returns: JSON processed page
        """
        if not page_url.endswith(".json"):
            page_url += ".json"
        response = self._request(page_url, params, url_data)
        if as_objects:
            hook = self._json_reddit_objecter
        else:
            hook = None
        return json.loads(response, object_hook=hook)

    def _json_reddit_objecter(self, json_data):
        """
        Object hook to be used with json.load(s) to spit out RedditObjects while
        decoding.
        """
        kind = json_data.get("kind")

        for reddit_object in (Comment, Redditor, Subreddit, Submission):
            if kind == reddit_object.kind:
                return reddit_object.from_api_response(self, json_data.get("data"))
        return json_data

    @property
    @require_login
    def content_id(self):
        """
        For most purposes, we can stretch things a bit and just make believe
        this object is the user (and return it's content_id instead of none.)
        """
        return self.user.content_id

    def _found_place_holder(self, children, place_holder=None):
        """
        Helper function, checks if any of the children's id match placeholder.
        Rather useless, but allows breaking all the way out of a nested loop.
        """
        if not place_holder:
            return False
        for child in children:
            if child.id == place_holder:
                return True

    def _get_content(self, page_url, limit=DEFAULT_CONTENT_LIMIT,
                     url_data=None, place_holder=None, all_content=None):
        """A method to return Reddit content from a URL. Starts at the initial
        page_url, and fetches content using the `after` JSON data until `limit`
        entries have been fetched, or the `place_holder` has been reached.

        :param page_url: the url to start fetching content from
        :param limit: the maximum number of content entries to fetch. if None,
            then fetch unlimited entries--this would be used in conjunction with
            the place_holder param.
        :param url_data: extra GET data to put in the url
        :param place_holder: if not None, the method will fetch `limit`
            content, stopping if it finds content with `id` equal to
            `place_holder`.
        :param all_content: the current list of content (used for recursion)
        :type place_holder: a string corresponding to a Reddit content id, e.g.
            't3_asdfasdf'
        :returns: a list of Reddit content, of type Subreddit, Comment, or
            Submission
        """
        if not url_data:
            url_data = {}
        if not all_content:
            # The list which we will populate to return with content
            all_content = []

        # While we still need to fetch more content to reach our limit, do so.
        while limit and len(all_content) < limit:
            # If the after variable isn't None, add it do the URL of the page
            # we are going to fetch.
            page_data = self._request_json(page_url, url_data=url_data)

            # if for some reason we didn't get data, then break
            try:
                data = page_data["data"]
            except KeyError:
                break

            after = data.get('after')
            children = data.get('children')
            all_content.extend(children)

            if self._found_place_holder(children, place_holder) or not after:
                break

            url_data["after"] = after
            self._get_content(page_url, limit, url_data, place_holder,
                              all_content)

        # we may have in the last iteration gotten a few extra results, so trim
        # down to limit
        if limit:
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
        data = self._request(URL)
        match = re.search(r"modhash[^,]*", data)
        self.modhash = match.group(0).split(": ")[1].strip(" '")

    def get_redditor(self, user_name, *args, **kwargs):
        """Return a Redditor class for the user_name specified."""
        return Redditor(self, user_name, *args, **kwargs)

    def get_subreddit(self, subreddit_name, *args, **kwargs):
        """Returns a Subreddit class for the user_name specified."""
        return Subreddit(self, subreddit_name, *args, **kwargs)

    @url(API_URL + "/login")
    def _login(self, user, password):
        return {'id' : '#login_login-main',
                'op' : 'login-main',
                'passwd' : password,
                'user' : user}

    def login(self, user=None, password=None):
        """Login to Reddit. If no user or password is provided, the user will
        be prompted with raw_input and getpass.getpass.
        """
        # Prompt user for necessary fields.
        if not user:
            user = raw_input("Username: ")
        if not password:
            import getpass
            password = getpass.getpass("Password: ")

        self._login(user, password)
        self.user = self.get_redditor(user)
        # Get and store the modhash; it will be needed for API requests
        # which involve this user.
        self._fetch_modhash()

    @url(REDDIT_URL + "/logout")
    @require_login
    def logout(self):
        """
        Logs out of a session.
        """
        self.user = None
        return {"uh" : self.modhash}

    @url(API_URL + "/vote")
    @require_login
    def _vote(self, content_id, direction=0, subreddit_name=""):
        """If logged in, vote for the given content_id in the direction
        specified."""
        return {'id' : content_id,
                'dir' : direction,
                'r' : subreddit_name,
                'uh' : self.modhash}

    @url()
    @require_login
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
        return self._request(URL, params)

    @url(API_URL + "/subscribe")
    @require_login
    def _subscribe(self, subreddit_id, unsubscribe=False):
        """If logged in, subscribe to the specified subreddit_id."""
        action = 'sub'
        if unsubscribe:
            action = 'unsub'
        return {'sr': subreddit_id,
                'action': action,
                'uh': self.modhash}

    @url(API_URL + "/comment")
    @require_login
    def _comment(self, content_id, subreddit_name=None, text=""):
        """Comment on the given content_id with the given text."""
        return {'thing_id': content_id,
                'text': text,
                'uh': self.modhash,
                'r': subreddit_name}

    def get_front_page(self, *args, **kwargs):
        """Return the reddit front page. Login isn't required, but you'll only
        see your own front page if you are logged in."""
        return self._get_content(REDDIT_URL + "/")

    @require_login
    def get_saved_links(self, limit=DEFAULT_CONTENT_LIMIT):
        """Return a listing of the logged-in user's saved links."""
        URL = REDDIT_URL + "/saved"
        return self._get_content(URL, limit=limit)

    def get_comments(self, limit=DEFAULT_CONTENT_LIMIT,
                     place_holder=None):
        """Returns a listing from reddit.com/comments"""
        URL = REDDIT_URL + "/comments"
        return self._get_content(URL, limit=limit, place_holder=place_holder)

    def _get_submission_comments(self, submission_url):
        json_data = self._request_json(submission_url)
        main_content = json_data[0] # this isn't used
        json_comments = json_data[1]['data']['children']

        comments = map(self._json_data_to_comment, json_comments)
        return comments

    def _json_data_to_comment(self, json_dict):
        data = json_dict['data']
        replies = data.pop('replies', None)

        root_comment = Comment(self, data)

        if replies:
            children = replies['data']['children']

            converted_children = map(self._json_data_to_comment, children)
            root_comment.replies = converted_children
        return root_comment

    def info(self, url=None, url_id=None):
        """
        Query the API to see if the given URL has been submitted already, and
        if it has, return the submissions.

        One and only one out of url (a url string) and url_id (a reddit url id)
        is required.
        """
        if bool(url) == bool(url_id):
            # either both or neither were given, either way:
            raise TypeError("One (and only one) of url or url_id is required!")
        URL = REDDIT_URL + "/button_info"
        if url:
            params = {"url" : url}
        else:
            params = {"id" : url_id}
        return self._get_content(URL, url_data=params)

    @url(API_URL + "/search_reddit_names", json=True)
    def _search_reddit_names(self, query):
        return {"query" : query}

    def search_reddit_names(self, query):
        results = self._search_reddit_names(query)
        return [self.get_subreddit(name) for name in results.get("names")]

    @url(API_URL + "/feedback")
    @require_captcha
    def send_feedback(self, name, email, message, reason="feedback"):
        return {"name" : name,
                "email" : email,
                "reason" : reason,
                "text" : message}

    @url(API_URL + "/submit")
    @require_captcha
    @require_login
    def submit(self, subreddit, url, title):
        """
        Submit a new link.

        Accepts either a Subreddit object or a str containing the subreddit
        name.
        """
        sr_name = str(subreddit)

        return {"kind" : "link",
                "sr" : sr_name,
                "title" : title,
                "uh" : self.modhash,
                "url" : url,
                "id" : self.user.id}

class Redditor(RedditContentObject):
    """A class for Redditor methods."""

    kind = "t2"

    get_overview = _get_section("/")
    get_comments = _get_section("/comments")
    get_submitted = _get_section("/submitted")

    def __init__(self, reddit_session, user_name=None, json_dict=None,
                 fetch=True):
        self.user_name = user_name
        # Store the urls we will need internally
        self.URL = REDDITOR_PAGE % self.user_name
        self.ABOUT_URL = REDDITOR_ABOUT_PAGE % self.user_name
        super(Redditor, self).__init__(reddit_session, user_name, json_dict,
                                       fetch)

    @limit_chars()
    def __str__(self):
        """Have the str just be the user's name"""
        return self.user_name

    @url(API_URL + "/register")
    @require_captcha
    @classmethod
    def _register(cls, password, email=""):
        """
        Register a new user.
        """
        password = str(password)
        return {"email" : email,
                "op" : "reg",
                "passwd" : password,
                "passwd2" : password,
                "user" : self.user_name}

    @classmethod
    def register(cls, password, email=""):
        cls._register(password, email)
        return self.reddit_session.login(self.user_name, password)

    create = register # just an alias to provide a somewhat uniform API

    @require_login
    def get_my_reddits(self, limit=DEFAULT_CONTENT_LIMIT):
        """Return all of the current user's subreddits."""
        URL = REDDIT_URL + "/reddits/mine"
        reddits = self._get_content(URL, limit=limit)
        return reddits

class Subreddit(RedditContentObject):
    """A class for Subreddits."""

    kind = "t5"

    ban = _modify_relationship("banned")
    make_contributor = _modify_relationship("contributor")
    make_moderator = _modify_relationship("moderator")

    unban = _modify_relationship("banned", unlink=True)
    remove_contributor = _modify_relationship("contributor", unlink=True)
    remove_moderator = _modify_relationship("moderator", unlink=True)

    ban.__doc__ = "Ban the target user."
    make_contributor.__doc__ = \
       "Make the target user a contributor in the given subreddit."
    make_moderator.__doc__ = \
       "Make the target user a moderator in the given subreddit."

    unban.__doc__ = "Unban the target user."
    remove_contributor.__doc__ = \
       "Remove the target user from contributor status in the given subreddit."
    remove_moderator.__doc__ = \
       "Revoke the target user's moderator privileges in the given subreddit."

    get_hot = _get_sorter("/")
    get_controversial = _get_sorter("/controversial", time="day")
    get_new = _get_sorter("/new", sort="rising")
    get_top = _get_sorter("/top", time="day")

    def __init__(self, reddit_session, subreddit_name=None, json_dict=None,
                 fetch=True):
        self.URL = urljoin(REDDIT_URL, "r/" + subreddit_name)
        self.ABOUT_URL = self.URL + "/about"

        self.display_name = subreddit_name
        super(Subreddit, self).__init__(reddit_session, subreddit_name,
                                        json_dict, fetch)

    @limit_chars()
    def __str__(self):
        """Just display the subreddit name."""
        return self.display_name

    @url(API_URL + "/site_admin")
    @require_login
    def _create(title, description="", language="English [en]",
                type="public", content_options="any", other_options=None,
                domain=""):
        """
        Create a new subreddit.
        """
        # TODO: Implement the rest of the options.
        return {"name" : self.display_name,
                "title" : title,
                "type" : type,
                "uh" : self.reddit_session.modhash}

    @classmethod
    def create(cls, title, description="", language="English [en]",
               type="public", content_options="any", other_options=None,
               domain=""):
        return cls._create(title, description, language, type, content_options,
                    other_options, domain)

    def submit(self, *args, **kwargs):
        """
        Submit a new link.
        """
        return self.reddit_session.submit(self, *args, **kwargs)

    def subscribe(self):
        """If logged in, subscribe to the given subreddit."""
        return self.reddit_session._subscribe(self.name)

    def unsubscribe(self):
        """If logged in, unsubscribe from the given subreddit."""
        return self.reddit_session._subscribe(self.name,
                                              unsubscribe=True)

class Submission(RedditContentObject, Voteable):
    """A class for submissions to Reddit."""

    kind = "t3"

    def __init__(self, reddit_session, title=None, json_dict=None):
        super(Submission, self).__init__(reddit_session, title, json_dict,
                                         fetch=True)

    def __str__(self):
        return str(self.score) + " :: " + self.title

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

class Comment(RedditContentObject, Voteable):
    """A class for comments."""

    kind = "t1"

    def __init__(self, reddit_session, json_dict=None):
        super(Comment, self).__init__(reddit_session, None, json_dict, True)
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
