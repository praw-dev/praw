# This file is part of reddit_api.
# 
# reddit_api is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# reddit_api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with reddit_api.  If not, see <http://www.gnu.org/licenses/>.

from util import urljoin

class URLDict(object):
    def __init__(self, base_url, *args):
        """
        Builds a URL dictionary. `args` should be tuples of the form:
            `(url_prefix, {"url_name", "url_path"})`
        """
        self._base_url = base_url
        self._urls = {}

        for prefix, url_dict in args:
            full_prefix = urljoin(self._base_url, prefix)
            for name, url in url_dict.iteritems():
                self[name] = urljoin(full_prefix, url)

    def __getitem__(self, key):
        return self._urls[key]

    def __setitem__(self, key, value):
        self._urls[key] = value

    def group(self, *urls):
        return [v for v in (self[k] for k in urls)]

urls = URLDict("http://www.reddit.com/",
          ("", {"reddit_url" : "",
                "api_url" : "api/",
                "comments" : "comments/",
                "help" : "help/",
                "info" : "button_info",
                "logout" : "logout/",
                "my_reddits" : "reddits/mine/",
                "my_moderation" : "reddits/mine/moderator/",
                "inbox" : "message/inbox/",
                "saved" : "saved/",
                "view_captcha" : "captcha/",
                }),
          ("api/", {"comment" : "comment/",
                    "compose_message" : "compose/",
                    "del" : "del/", 
                    "friend" : "friend/",
                    "login" : "login/",
                    "new_captcha" : "new_captcha/",
                    "register" : "register/",
                    "save" : "save/",
                    "search_reddit_names" : "search_reddit_names/",
                    "send_feedback" : "feedback/",
                    "site_admin" : "site_admin/",
                    "submit" : "submit/",
                    "subscribe" : "subscribe/",
                    "unfriend" : "unfriend/",
                    "unsave" : "unsave/",
                    "vote" : "vote/",
                   }),
          ("r/", {"subreddit_base" : "",
                  "subreddit_page" : "%s/",
                  "subreddit_about_page" : "%s/about",
                 }),
          ("user/", {"redditor_page" : "%s/",
                     "redditor_about_page" : "%s/about/",
                    }))

# URL Groups:
urls.saved_links = urls.group("saved")
