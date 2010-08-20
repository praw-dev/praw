import urllib
import urllib2
import simplejson
import cookielib
import re

DEFAULT_CONTENT_LIMIT = 25

REDDIT_USER_AGENT = { 'User-agent': 'Mozilla/4.0 (compatible; MSIE5.5; Windows NT' }
REDDIT_URL = "http://www.reddit.com/"
REDDIT_LOGIN_URL = REDDIT_URL + "api/login"
REDDIT_VOTE_URL = REDDIT_URL + "api/vote"
REDDIT_SAVE_URL = REDDIT_URL + "api/save"
REDDIT_UNSAVE_URL = REDDIT_URL + "api/unsave"
REDDIT_COMMENT_URL = REDDIT_URL + "api/comment"
REDDIT_SUBSCRIBE_URL = REDDIT_URL + "api/subscribe"
REDDIT_COMMENTS_URL = REDDIT_URL + "comments"
MY_REDDITS_URL = REDDIT_URL + "reddits/mine"
REDDIT_SAVED_LINKS = REDDIT_URL + "saved"
# A small site to fetch the modhash
REDDIT_URL_FOR_MODHASH = "http://www.reddit.com/help"

REDDITOR_PAGE = "http://www.reddit.com/user/%s"
REDDITOR_ABOUT_PAGE = REDDITOR_PAGE + "/about"
REDDITOR_ABOUT_FIELDS = ['comment_karma', 'created', 'created_utc', 'has_mail', 'has_mod_mail', 'id', 'is_mod', 'link_karma', 'name']
SUBREDDIT_ABOUT_FIELDS = ['display_name', 'name', 'title', 'url', 'created', 'created_utc', 'over18', 'subscribers', 'id', 'description']
SUBREDDIT_SECTIONS = ['hot', 'new', 'controversial', 'top']


class Reddit:
    """A class for a reddit session."""
    def __init__(self):
        """Initialize all of the tools we need."""
        # Make these simpler to access
        self.Request = urllib2.Request
        self.urlopen = urllib2.urlopen

        # Set cookies
        self.cookie_jar = cookielib.CookieJar()
        opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.cookie_jar))
        urllib2.install_opener(opener)

        # Set logged in user to None
        self.user = None

    def get_page(self, page_url, params=None, url_data=None):
        """Given a page url and a dict of params, return the page JSON."""
        # Add .JSON to the end of the url
        page_url += ".json"
        if url_data is not None:
            page_url += "?"+urllib.urlencode(url_data)
        
        # Encode the params and then create the request.
        encoded_params = None
        if params is not None:
            encoded_params = urllib.urlencode(params)
        request = self.Request(page_url, 
                               encoded_params, 
                               REDDIT_USER_AGENT)
        # Get the data 
        json_data = self.urlopen(request).read()
        data = simplejson.loads(json_data)

        return data
    def get_content(self, page_url, limit=DEFAULT_CONTENT_LIMIT, 
                    url_data=None, place_holder=None):
        all_content = []
        after = None
        print "Entering loop"
        print "limit: " + str(limit)
        
        while len(all_content) < limit or limit == -1:
            print "At Start of loop"
            print "len: " + str(len(all_content))
            if after is not None:
                print "after: " + after

            if after is not None:
                data = {"after":after}
                if url_data is not None:
                    data.update(url_data)
                page_data = self.get_page(page_url, url_data=data)
            else:
                page_data = self.get_page(page_url, url_data=url_data)

            if page_data.get('data') is None:
                print "data is none"
                break

            data = page_data.get('data')
            children = data.get('children')

            found_place_holder=False

            print "iterating through children"
            for child in children:
                print "child: " + str(child.get('data').get('name'))
                if place_holder is not None and \
                   child.get('data').get('name') == place_holder:
                    print "found place  holder"
                    found_place_holder=True
                    break

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
            
            if after is None:
                print "after is None, exiting"
                break

            if found_place_holder is True:
                print "found place holder, exiting main loop"
                break

        if limit != -1:
            all_content = all_content[:limit]

        return all_content

    def get_user(self, user_name):
        return Redditor(user_name, self)
    def get_subreddit(self, subreddit_name):
        return Subreddit(subreddit_name, self)

    def login(self, user=None, password=None):
        if user is not None and password is None:
            import getpass
            password = getpass.getpass("Password: ")
        self.user = user

        params = urllib.urlencode({
                    'id' : '#login_login-main',
                    'op' : 'login-main',
                    'passwd' : password,
                    'user' : user
                })
        req = self.Request(REDDIT_LOGIN_URL, params, REDDIT_USER_AGENT)
        data =  self.urlopen(req).read()

        # Get and store the modhash now that we can
        self.fetch_modhash()

        return data
    def fetch_modhash(self):
        req = self.Request(REDDIT_URL_FOR_MODHASH, 
                           None, REDDIT_USER_AGENT)
        # Should only need ~1200 chars to get the modhash
        data = self.urlopen(req).read(1200)
        match = re.search(r"modhash[^,]*", data)
        self.modhash = eval(match.group(0).split(": ")[1])

    def vote(self, content_id, direction=0, subreddit_name=""):
        params = urllib.urlencode({
                    'id' : content_id,
                    'dir' : direction,
                    'r' : subreddit_name,
                    'uh' : self.modhash
                })
        req = self.Request(REDDIT_VOTE_URL, params, REDDIT_USER_AGENT)
        return self.urlopen(req).read()
    def save(self, content_id, unsave=False):
        url = REDDIT_SAVE_URL
        executed = 'saved'
        if unsave is True:
            executed = 'unsaved'
            url = REDDIT_UNSAVE_URL
        params = urllib.urlencode({
                    'id': content_id,
                    'executed': executed,
                    'uh': self.modhash
            })
        req = self.Request(url, params, REDDIT_USER_AGENT)
        return self.urlopen(req).read()
    def subscribe(self, subreddit_id, unsubscribe=False):
        action = 'sub'
        if unsubscribe is True:
            action = 'unsub'
        params = urllib.urlencode({
                    'sr': subreddit_id,
                    'action': action,
                    'uh': self.modhash
            })
        req = self.Request(REDDIT_SUBSCRIBE_URL, params, 
                           REDDIT_USER_AGENT)
        return self.urlopen(req).read()
    def get_my_reddits(self, limit=DEFAULT_CONTENT_LIMIT):
        reddits = self.get_content(MY_REDDITS_URL, 
                                   limit=limit)
        return reddits
    def comment(self, content_id, subreddit_name=None, text=""):
        url = REDDIT_COMMENT_URL
        params = urllib.urlencode({
                    'thing_id': content_id,
                    'text': text,
                    'uh': self.modhash,
                    'r': subreddit_name
            })
        req = self.Request(url, params, REDDIT_USER_AGENT)
        return self.urlopen(req).read()
    def friend(self, user):
        url = "http://www.reddit.com/api/friend"
        params = urllib.urlencode({
                    'name': user,
                    'container': self.user,
                    'uh': self.modhash
                    #'type': 'friend'
            })
        req = self.Request(url, params, REDDIT_USER_AGENT)
        return self.urlopen(req).read()

    def get_home_page(self):
        return RedditPage("http://www.reddit.com","reddit.com", self)
    def get_saved_links(self, limit=-1):
        return self.get_content(REDDIT_SAVED_LINKS, limit=limit)
    def get_comments(self, limit=DEFAULT_CONTENT_LIMIT,
                     place_holder=None):
        url = REDDIT_COMMENTS_URL
        return self.get_content(url, limit=limit, 
                                place_holder=place_holder)


        
class Redditor:
    """A class for Redditor methods."""
    def __init__(self, user_name, reddit_session):
        self.user_name = user_name
        self.URL = REDDITOR_PAGE % self.user_name
        self.ABOUT_URL = REDDITOR_ABOUT_PAGE % self.user_name
        self.reddit_session = reddit_session
    def __repr__(self):
        return self.user_name

    def get_about_attribute(self, attribute):
        data = self.reddit_session.get_page(self.ABOUT_URL)
        return data['data'].get(attribute)
    def get_overview(self, sort="new", time="all", 
                     limit=DEFAULT_CONTENT_LIMIT, 
                     place_holder=None):
        url = self.URL
        url_data = {"sort": sort, "time":time}
        return self.reddit_session.get_content(url, limit=limit, 
                                               url_data=url_data,
                                               place_holder=place_holder)
    def get_comments(self, sort="new", time="all", 
                     limit=DEFAULT_CONTENT_LIMIT,
                     place_holder=None):
        url = self.URL + "/comments"
        url_data = {"sort": sort, "time":time}
        return self.reddit_session.get_content(url, limit=limit, 
                                               url_data=url_data,
                                               place_holder=place_holder)
    def get_submitted(self, sort="new", time="all", 
                      limit=DEFAULT_CONTENT_LIMIT,
                      place_holder=None):
        url = self.URL + "/submitted"
        url_data = {"sort": sort, "time":time}
        return self.reddit_session.get_content(url, limit=limit, 
                                               url_data=url_data,
                                               place_holder=place_holder)

# Add getters for Redditor about fields
for user_attribute in REDDITOR_ABOUT_FIELDS:
    func = lambda self, attribute=user_attribute: \
            self.get_about_attribute(attribute)
    setattr(Redditor, user_attribute, property(func))
        
class RedditPage:
    def __init__(self, url, name, reddit_session):
        self.URL = url
        self.display_name = name
        self.reddit_session = reddit_session
    def __repr__(self):
        return self.display_name
    def get_top(self, time="day", limit=DEFAULT_CONTENT_LIMIT,
               place_holder=None):
        url = self.URL + "/top"
        url_data = {"t":time}
        return self.reddit_session.get_content(url, limit=limit, 
                                               url_data=url_data,
                                              place_holder=place_holder)
    def get_controversial(self, time="day", limit=DEFAULT_CONTENT_LIMIT,
                         place_holder=None):
        url = self.URL + "/controversial"
        url_data = {"t":time}
        return self.reddit_session.get_content(url, limit=limit, 
                                               url_data=url_data,
                                              place_holder=place_holder)
    def get_new(self, sort="rising", limit=DEFAULT_CONTENT_LIMIT,
               place_holder=None):
        url = self.URL + "/new"
        url_data = {"sort":sort}
        return self.reddit_session.get_content(url, limit=limit, 
                                               url_data=url_data,
                                              place_holder=place_holder)
    def get_hot(self, limit=DEFAULT_CONTENT_LIMIT,
               place_holder=None):
        url = self.URL
        if url[-1] != '/':
            url += '/'
        return self.reddit_session.get_content(url, limit=limit,
                                              place_holder=place_holder)

class Subreddit(RedditPage):
    def __init__(self, subreddit_name, reddit_session):
        self.name = subreddit_name
        self.URL = REDDIT_URL + "r/" + self.name
        self.ABOUT_URL = self.URL + "/about"
        self.reddit_session = reddit_session
    def __repr__(self):
        return self.display_name

    def get_top(self, time="day", limit=DEFAULT_CONTENT_LIMIT):
        top_url = self.URL + "/top"
        return self.reddit_session.get_content(top_url, 
                                               limit=limit, 
                                               url_data={"t":time})
    def get_controversial(self, time="day", 
                          limit=DEFAULT_CONTENT_LIMIT):
        controversial_url = self.URL + "/controversial"
        return self.reddit_session.get_content(top_url, 
                                               limit=limit, 
                                               url_data={"t":time})
    def get_new(self, sort="rising", limit=DEFAULT_CONTENT_LIMIT):
        new_url = self.URL + "/new"
        return self.reddit_session.get_content(top_url, 
                                               limit=limit, 
                                               url_data={"sort":sort})
    def get_hot(self, limit=DEFAULT_CONTENT_LIMIT):
        return self.reddit_session.get_content(self.URL, 
                                               limit=limit)
    def get_about_attribute(self, attribute):
        data = self.reddit_session.get_page(self.ABOUT_URL)
        return data['data'].get(attribute)
    def subscribe(self):
        return self.reddit_session.subscribe(self.get_name())
    def unsubscribe(self):
        return self.reddit_session.subscribe(self.get_name(), 
                                             unsubscribe=True)

# Add getters for Redditor about fields
for sr_attribute in SUBREDDIT_ABOUT_FIELDS:
    func = lambda self, attribute=sr_attribute: \
            self.get_about_attribute(attribute)
    setattr(Subreddit, sr_attribute, property(func))

class Submission:
    """A class for content on Reddit"""
    def __init__(self, json_dict, reddit_session):
        self.__dict__.update(json_dict)
        self.reddit_session = reddit_session
    def vote(self, direction=0):
        """Vote for this story."""
        return self.reddit_session.vote(self.name, 
                            direction=direction, 
                            subreddit_name=self.subreddit)
    def upvote(self):
        return self.vote(direction=1)
    def downvote(self):
        return self.vote(direction=-1)
    def __repr__(self):
        return (str(self.score) + " :: " + self.title)
    def save(self):
        return self.reddit_session.save(self.name)
    def unsave(self):
        return self.reddit_session.save(self.name, unsave=True)
    def comment(self, text):
        return self.reddit_session.comment(self.name,
                                           subreddit_name=self.subreddit,
                                           text=text)

class Comment:
    """A class for comments."""
    def __init__(self, json_dict, reddit_session):
        self.__dict__.update(json_dict)
        self.reddit_session = reddit_session
    def __repr__(self):
        # TODO: update this
        comment_string = self.body[:100]
        if len(self.body)>100:
            comment_string += "..."
        return comment_string
    def vote(self, direction=0):
        return self.reddit_session.vote(self.name,
                                        direction=direction,
                                        subreddit_name=self.subreddit)
    def upvote(self):
        return self.vote(direction=1)
    def downvote(self):
        return self.vote(direction=-1)
    def reply(self, text):
        return self.reddit_session.comment(self.name,
                                           subreddit_name=self.subreddit,
                                           text=text)
