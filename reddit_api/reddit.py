import urllib
import urllib2
import cookielib
import re
import time
import warnings
try:
    import json
except ImportError:
    import simplejson as json

from functools import wraps

from urls import urls
from util import urljoin, memoize, limit_chars

DEBUG = True

# How many results to retrieve by default when making content calls
DEFAULT_CONTENT_LIMIT = 25

class APIException(Exception):
    """Base exception class for these API bindings."""
    pass

class APIWarning(UserWarning):
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
    URL = urls["new_captcha"]
    VIEW_URL = urls["view_captcha"]

    def __init__(self, func):
        wraps(func)(self)
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
            return urljoin(self.VIEW_URL, self.captcha_id + ".png")

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

        if user is None:
            raise NotLoggedInException()
        else:
            return func(self, *args, **kwargs)
    return login_reqd_func

class sleep_after(object):
    """
    A decorator to add to API functions that shouldn't be called too
    rapidly, in order to be nice to the reddit server.

    Every function wrapped with this decorator will use a collective
    last_call_time attribute, so that collectively any one of the funcs won't
    be callable within the WAIT_BETWEEN_CALL_TIME; they'll automatically be
    delayed until the proper duration is reached.
    """
    WAIT_BETWEEN_CALL_TIME = 1          # seconds
    last_call_time = 0     # init to 0 to always allow the 1st call

    def __init__(self, func):
        wraps(func)(self)
        self.func = func

    def __call__(self, *args, **kwargs):
        call_time = time.time()

        since_last_call = call_time - self.last_call_time
        if since_last_call < self.WAIT_BETWEEN_CALL_TIME:
            time.sleep(self.WAIT_BETWEEN_CALL_TIME - since_last_call)

        self.__class__.last_call_time = call_time
        return self.func(*args, **kwargs)

def parse_api_json_response(func):
    """Decorator to look at the Reddit API response to an API POST request like
    vote, subscribe, login, etc. Basically, it just looks for certain errors in
    the return string. If it doesn't find one, then it just returns True.
    """
    @wraps(func)
    def error_checked_func(*args, **kwargs):
        return_value = func(*args, **kwargs)
        if not return_value:
            return
        elif [k for k in return_value.keys() if k not in
                               (u"jquery", "iden", "captcha", "kind", "data")]:
                warnings.warn("Return value keys contained "
                              "{0}!".format(return_value.keys()))
        else:
            jquery = return_value.get("jquery")
            if jquery:
                values = [x[-1] for x in jquery]
                if [".error.USER_REQUIRED"] in values:
                    raise NotLoggedInException()
        return return_value
    return error_checked_func

def _get_section(subpath=""):
    """
    Used by the Redditor class to generate each of the sections (overview,
    comments, submitted).
    """
    def get_section(self, sort="new", time="all", limit=DEFAULT_CONTENT_LIMIT,
                    place_holder=None):
        url_data = {"sort" : sort, "time" : time}
        return self.reddit_session._get_content(urljoin(self.URL, subpath),
                                                limit=limit,
                                                url_data=url_data,
                                                place_holder=place_holder)
    return get_section

def _get_sorter(subpath="", **defaults):
    """
    Used by the Reddit Page classes to generate each of the currently supported
    sorts (hot, top, new, best).
    """
    def sorted(self, limit=DEFAULT_CONTENT_LIMIT, place_holder=None, **data):
        for k, v in defaults.items():
            if k == "time":
                # time should be "t" in the API data dict
                k = "t"
            data.setdefault(k, v)
        return self.reddit_session._get_content(urljoin(self.URL, subpath),
                                                limit=int(limit),
                                                url_data=data,
                                                place_holder=place_holder)
    return sorted

def _modify_relationship(relationship, unlink=False):
    """
    Modify the relationship between the current user or subreddit and a target
    thing.

    Used to support friending (user-to-user), as well as moderating,
    contributor creating, and banning (user-to-subreddit).
    """
    # the API uses friend and unfriend to manage all of these relationships
    url = urls["unfriend" if unlink else "friend"]

    @require_login
    def do_relationship(self, thing):
        params = {'name': thing,
                  'container': self.content_id,
                  'type': relationship,
                  'uh': self.modhash}
        return self._request_json(url, params)
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
        if name is None and json_dict is None:
            # one of these at least is required
            raise TypeError("Either the name or json dict is required!.")

        self.reddit_session = reddit_session

        if json_dict is None:
            if fetch:
                json_dict = self._get_json_dict()
            else:
                json_dict = {}
        for name, value in json_dict.iteritems():
            setattr(self, name, value)

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
                for name, value in json_dict.iteritems():
                    setattr(self, name, value)
                self._populated = True
                return getattr(self, attr)
        raise AttributeError("'{0}' object has no attribute '{1}'".format(
                                                self.__class__.__name__, attr))

    def __setattr__(self, name, value):
        if name == "subreddit":
            value = Subreddit(self.reddit_session, value, fetch=False)
        elif name == "redditor" or name == "author":
            value = Redditor(self.reddit_session, value, fetch=False)
        object.__setattr__(self, name, value)

    def __eq__(self, other):
        return self.content_id == other.content_id

    def __ne__(self, other):
        return self.content_id != other.content_id

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

class Saveable(object):
    """
    Additional interface for Reddit content objects that can be saved.
    Currently only Submissions, but this may change at a later date, as
    eventually Comments will probably end up being saveable.
    """
    @require_login
    def save(self, unsave=False):
        """If logged in, save the content specified by `content_id`."""
        url = urls["unsave" if unsave else "save"]
        params = {'id': self.name,
                  'executed': "unsaved" if unsave else "saved",
                  'uh': self.reddit_session.modhash}
        response = self.reddit_session._request_json(url, params)
        _request.is_stale(urls.saved_links)

    def unsave(self):
        return self.save(unsave=True)
        
class Deletable(object):
    """
    Additional Interface for Reddit content objects that can be deleted
    (currently Submission and Comment).
    """
    def delete(self):
        url = urls["del"]
        params = {'id' : self.name,
                    'executed' : 'deleted',  
                    'r' : self.subreddit, 
                    'uh' : self.reddit_session.modhash}
        return self.reddit_session._request_json(url, params)

class Voteable(object):
    """
    Additional interface for Reddit content objects that can be voted on
    (currently Submission and Comment).
    """
    @require_login
    def vote(self, direction=0):
        """
        Vote for the given content_id in the direction specified.
        """
        url = urls["vote"]
        params = {'id' : self.name,
                  'dir' : direction,
                  'r' : self.subreddit,
                  'uh' : self.reddit_session.modhash}
        return self.reddit_session._request_json(url, params)

    def upvote(self):
        return self.vote(direction=1)

    def downvote(self):
        return self.vote(direction=-1)

class Reddit(RedditObject):
    """A class for a reddit session."""
    DEFAULT_HEADERS = {}

    friend = _modify_relationship("friend")
    friend.__doc__ = "Friend the target user."

    unfriend = _modify_relationship("friend", unlink=True)
    unfriend.__doc__ = "Unfriend the target user."

    def __init__(self, user_agent=None):
        if user_agent is None:
            if DEBUG:
                user_agent = "Reddit API Python Wrapper (Debug Mode)"
            else:
                raise APIException("You need to set a user_agent to identify "
                                   "your application!")
        self.DEFAULT_HEADERS["User-agent"] = user_agent

        self._cookie_jar = cookielib.CookieJar()
        opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self._cookie_jar))
        urllib2.install_opener(opener)

        self.user = None

    def __str__(self):
        return "Open Session (%s)" % (self.user or "Unauthenticated")

    def _request(self, page_url, params=None, url_data=None):
        """Given a page url and a dict of params, opens and returns the page.

        :param page_url: the url to grab content from.
        :param params: the extra url data to submit
        :param url_data: the GET data to put in the url
        :returns: the open page
        """
        return _request(self, page_url, params, url_data)

    @parse_api_json_response
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
        # TODO: This can be nicer. CONTENT_KINDS dict.
        kinds = dict((content.kind, content) for content in
                                    (Comment, Redditor, Subreddit, Submission))
        try:
            kind = kinds[json_data["kind"]]
        except KeyError:
            pass
        else:
            return kind.from_api_response(self, json_data["data"])
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
        if place_holder is None:
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
        if url_data is None:
            url_data = {}
        if all_content is None:
            # The list which we will populate to return with content
            all_content = []
        if limit is not None:
            limit = int(limit)

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
        # TODO: find the right modhash url, this is only temporary
        URL = urls["help"]
        data = self._request(URL)
        match = re.search(r"modhash[^,]*", data)
        self.modhash = match.group(0).split(": ")[1].strip(" '")

    def get_redditor(self, user_name, *args, **kwargs):
        """Return a Redditor class for the user_name specified."""
        return Redditor(self, user_name, *args, **kwargs)

    def get_subreddit(self, subreddit_name, *args, **kwargs):
        """Returns a Subreddit class for the user_name specified."""
        return Subreddit(self, subreddit_name, *args, **kwargs)

    def login(self, user=None, password=None):
        """Login to Reddit. If no user or password is provided, the user will
        be prompted with raw_input and getpass.getpass.
        """
        # Prompt user for necessary fields.
        if user is None:
            user = raw_input("Username: ")
        if password is None:
            import getpass
            password = getpass.getpass("Password: ")

        url = urls["login"]
        params = {'id' : '#login_login-main',
                  'op' : 'login-main',
                  'passwd' : password,
                  'user' : user}
        self._request_json(url, params)
        self.user = self.get_redditor(user)
        # Get and store the modhash; it will be needed for API requests
        # which involve this user.
        self._fetch_modhash()

    @require_login
    def logout(self):
        """
        Logs out of a session.
        """
        self.user = None
        url = urls["logout"]
        params = {"uh" : self.modhash}
        return self._request_json(url, params)

    @require_login
    def _subscribe(self, subreddit_id, unsubscribe=False):
        """If logged in, subscribe to the specified subreddit_id."""
        action = "unsub" if unsubscribe else "sub"
        url = urls["subscribe"]
        params = {'sr': subreddit_id,
                  'action': action,
                  'uh': self.modhash}
        return self._request_json(url, params)

    @require_login
    def _add_comment(self, content_id, subreddit_name=None, text=""):
        """Comment on the given content_id with the given text."""
        url = urls["comment"]
        params = {'thing_id': content_id,
                  'text': text,
                  'uh': self.modhash,
                  'r': subreddit_name}
        self._request_json(url, params)

    def get_front_page(self, limit=DEFAULT_CONTENT_LIMIT):
        """Return the reddit front page. Login isn't required, but you'll only
        see your own front page if you are logged in."""
        return self._get_content(urls["reddit_url"], limit=limit)

    @require_login
    def get_saved_links(self, limit=DEFAULT_CONTENT_LIMIT):
        """Return a listing of the logged-in user's saved links."""
        return self._get_content(urls["saved"], limit=limit)

    def get_all_comments(self, limit=DEFAULT_CONTENT_LIMIT, place_holder=None):
        """Returns a listing from reddit.com/comments (which provides all of
        the most recent comments from all users to all submissions)."""
        return self._get_content(urls["comments"], limit=limit, place_holder=place_holder)

    def info(self, url=None, id=None, limit=DEFAULT_CONTENT_LIMIT):
        """
        Query the API to see if the given URL has been submitted already, and
        if it has, return the submissions.

        One and only one out of url (a url string) and id (a reddit url id) is
        required.
        """
        if bool(url) == bool(id):
            # either both or neither were given, either way:
            raise TypeError("One (and only one) of url or id is required!")
        if url is not None:
            params = {"url" : url}

            if url.startswith(urls["reddit_url"]) and url != urls["reddit_url"]:
                warnings.warn("It looks like you may be trying to get the info"
                              " of a self or internal link. This probably "
                              "won't return any useful results!", APIWarning)
        else:
            params = {"id" : id}
        return self._get_content(urls["info"], url_data=params, limit=limit)

    @require_captcha
    def send_feedback(self, name, email, message, reason="feedback"):
        """
        Send feedback to the admins. Please don't abuse this, read what it says
        on the send feedback page!
        """
        url = urls["send_feedback"]
        params = {"name" : name,
                  "email" : email,
                  "reason" : reason,
                  "text" : message}
        return self._request_json(url, params)

    @require_login
    @require_captcha
    def compose_message(self, recipient, subject, message):
        """
        Send a message to another redditor.
        """
        url = urls["compose_message"]
        params = {"text" : message,
                  "subject" : subject,
                  "to" : str(recipient),
                  "uh" : self.modhash,
                  "user" : self.user}
        return self._request_json(url, params)

    def search_reddit_names(self, query):
        """
        Search the subreddits for a reddit whose name matches the query.
        """
        url = urls["search_reddit_names"]
        params = {"query" : query}
        results = self._request_json(url, params)
        return [self.get_subreddit(name) for name in results.get("names")]

    @require_login
    @require_captcha
    def submit(self, subreddit, url, title, submit_type=None, text=None):
        """
        Submit a new link.

        Accepts either a Subreddit object or a str containing the subreddit
        name.
        """
        sr_name = str(subreddit)

        params = {"kind" : "link",
                  "sr" : sr_name,
                  "title" : title,
                  "uh" : self.modhash,
                  "url" : url,
                  "id" : self.user.id}
        if submit_type == 'self' and text != None:
            params["kind"] = submit_type
            params["text"] = text
            del(params["url"])
        url = urls["submit"]
        return self._request_json(url, params)

class Redditor(RedditContentObject):
    """A class for Redditor methods."""

    kind = "t2"

    get_overview = _get_section("/")
    get_comments = _get_section("/comments")
    get_submitted = _get_section("/submitted")

    def __init__(self, reddit_session, user_name=None, json_dict=None,
                 fetch=False):
        self.user_name = user_name
        # Store the urls we will need internally
        self.URL = urls["redditor_page"] % self.user_name
        self.ABOUT_URL = urls["redditor_about_page"] % self.user_name
        super(Redditor, self).__init__(reddit_session, user_name, json_dict,
                                       fetch)

    @limit_chars()
    def __str__(self):
        """Have the str just be the user's name"""
        return self.user_name.encode("utf8")

    @classmethod
    @require_captcha
    def register(cls, password, email=""):
        """
        Register a new user.
        """
        password = str(password)
        url = urls["register"]
        params = {"email" : email,
                  "op" : "reg",
                  "passwd" : password,
                  "passwd2" : password,
                  "user" : self.user_name}
        self._request_json(url, params)
        return self.reddit_session.login(self.user_name, password)

    create = register # just an alias to provide a somewhat uniform API

    @require_login
    def get_my_reddits(self, limit=DEFAULT_CONTENT_LIMIT):
        """Return all of the current user's subreddits."""
        return self._get_content(urls["my_reddits"], limit=limit)

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
                 fetch=False):
        self.URL = urls["subreddit_page"] % subreddit_name
        self.ABOUT_URL = urls["subreddit_about_page"] % subreddit_name

        self.display_name = subreddit_name
        super(Subreddit, self).__init__(reddit_session, subreddit_name,
                                        json_dict, fetch)

    @limit_chars()
    def __str__(self):
        """Just display the subreddit name."""
        return self.display_name.encode("utf8")

    @classmethod
    @require_login
    def create(cls, title, description="", language="English [en]",
               type="public", content_options="any", other_options=None,
               domain=""):
        """
        Create a new subreddit.
        """
        url = urls["create"]
        # TODO: Implement the rest of the options.
        params = {"name" : self.display_name,
                  "title" : title,
                  "type" : type,
                  "uh" : self.reddit_session.modhash}
        return self._request_json(url, params)

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

class Submission(RedditContentObject, Saveable, Voteable,  Deletable):
    """A class for submissions to Reddit."""

    kind = "t3"

    def __init__(self, reddit_session, title=None, json_dict=None,
                 fetch_comments=True):
        super(Submission, self).__init__(reddit_session, title, json_dict,
                                         fetch=True)
        if not self.permalink.startswith(urls["reddit_url"]):
            self.permalink = urljoin(urls["reddit_url"], self.permalink)

    def __str__(self):
        title = self.title.replace("\r\n", "")
        return "{0} :: {1}".format(self.score, title.encode("utf-8"))

    @property
    def comments(self):
        submission_info, comment_info = self.reddit_session._request_json(
                                                            self.permalink)
        comments = comment_info["data"]["children"]
        return comments

    def add_comment(self, text):
        """If logged in, comment on the submission using the specified text."""
        return self.reddit_session._add_comment(self.name,
                                                subreddit_name=self.subreddit,
                                                text=text)

class Comment(RedditContentObject, Voteable,  Deletable):
    """A class for comments."""

    kind = "t1"

    def __init__(self, reddit_session, json_dict):
        super(Comment, self).__init__(reddit_session, None, json_dict, True)
        if self.replies:
            self.replies = self.replies["data"]["children"]
        else:
            self.replies = []

    @limit_chars()
    def __str__(self):
        return getattr(self, "body",
                       "[[ need to fetch more comments... ]]").encode("utf8")

    @property
    def is_root(self):
        return not bool(getattr(self, "parent", False))

    def reply(self, text):
        """Reply to the comment with the specified text."""
        return self.reddit_session._add_comment(self.name,
                                                subreddit_name=self.subreddit,
                                                text=text)

@memoize
@sleep_after
def _request(reddit_session, page_url, params=None, url_data=None):
        if url_data:
            page_url += "?" + urllib.urlencode(url_data)

        # urllib2.Request throws a 404 for some reason with data=""
        encoded_params = None
        if params:
            encoded_params = urllib.urlencode(params)

        request = urllib2.Request(page_url,
                                  data=encoded_params,
                                  headers=reddit_session.DEFAULT_HEADERS)
        response = urllib2.urlopen(request)
        return response.read()
