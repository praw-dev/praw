import urllib
import urllib2
import simplejson
import cookielib

DEFAULT_CONTENT_LIMIT = 25

REDDIT_USER_AGENT = { 'User-agent': 'Mozilla/4.0 (compatible; MSIE5.5; Windows NT' }
REDDIT_URL = "http://www.reddit.com/"
REDDIT_LOGIN_URL = "http://www.reddit.com/api/login"
REDDIT_VOTE_URL = "http://www.reddit.com/api/vote"

REDDITOR_ABOUT_PAGE = "http://www.reddit.com/user/%s/about"
REDDITOR_ABOUT_FIELDS = ['comment_karma', 'created', 'created_utc', 'has_mail', 'has_mod_mail', 'id', 'is_mod', 'link_karma', 'name']
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
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
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
        request = self.Request(page_url, encoded_params, REDDIT_USER_AGENT)

        # Get the data 
        json_data = self.urlopen(request).read()
        data = simplejson.loads(json_data)

        return data

    def get_user(self, user_name):
        return Redditor(user_name, self)
    def get_subreddit(self, subreddit_name):
        return Subreddit(subreddit_name, self)

    def get_content(self, page_url, limit=DEFAULT_CONTENT_LIMIT, url_data=None):
        content = []
        after = None
        
        while len(content) < limit:
            if after is not None:
                data = {"after":after}
                if url_data is not None:
                    data.extend(url_data)
                page_data = self.get_page(page_url, url_data=data)
            else:
                page_data = self.get_page(page_url, url_data=url_data)

            if page_data.get('data') is None:
                break

            data = page_data.get('data')

            children = map(lambda x: x.get('data'), data.get('children'))
            content.extend(children)
            after = data.get('after')
            
            if after is None:
                break

        content = content[:limit]

        return content
    def login(self, user, password):
        self.user = user

        params = urllib.urlencode({
                    'id' : '#login_login-main',
                    'op' : 'login-main',
                    'passwd' : password,
                    'user' : user
                })
        req = self.Request(REDDIT_LOGIN_URL, params, REDDIT_USER_AGENT)
        return self.urlopen(req).read()
    def vote(self, content_id, direction=0, subreddit_name=""):
        params = urllib.urlencode({
                    'id' : content_id,
                    'dir' : direction,
                    'r' : subreddit_name
                })
        req = self.Request(REDDIT_VOTE_URL, params, REDDIT_USER_AGENT)
        return self.urlopen(req).read()
        
class Redditor:
    """A class for Redditor methods."""
    def __init__(self, user_name, reddit_session):
        self.user_name = user_name
        self.ABOUT_URL = REDDITOR_ABOUT_PAGE % self.user_name
        self.reddit_session = reddit_session

    def get_about_attribute(self, attribute):
        data = self.reddit_session.get_page(self.ABOUT_URL)
        return data['data'].get(attribute)

# Add getters for Redditor about fields
for user_attribute in REDDITOR_ABOUT_FIELDS:
    func = lambda self, attribute=user_attribute: self.get_about_attribute(attribute)
    setattr(Redditor, 'get_'+user_attribute, func)
        
class Subreddit:
    def __init__(self, subreddit_name, reddit_session):
        self.name = subreddit_name
        self.url = REDDIT_URL + "r/" + self.name
        self.reddit_session = reddit_session
    def get_top(self, time="day", limit=DEFAULT_CONTENT_LIMIT):
        top_url = self.url + "/top"
        return self.reddit_session.get_content(top_url, limit=limit, url_data={"t":time})
    def get_controversial(self, time="day", limit=DEFAULT_CONTENT_LIMIT):
        controversial_url = self.url + "/controversial"
        return self.reddit_session.get_content(top_url, limit=limit, url_data={"t":time})
    def get_new(self, sort="rising", limit=DEFAULT_CONTENT_LIMIT):
        new_url = self.url + "/new"
        return self.reddit_session.get_content(top_url, limit=limit, url_data={"sort":sort})
    def get_hot(self, limit=DEFAULT_CONTENT_LIMIT):
        return self.reddit_session.get_content(self.url, limit=limit)


        
        





