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

from decorators import require_login, sleep_after
from util import memoize, urljoin
from settings import DEFAULT_CONTENT_LIMIT
from urls import urls
import urllib
import urllib2


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
                                                limit=limit,
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
                  'container': self.content_id, # this will return the user id
                  'type': relationship,
                  'uh': self.modhash}
        return self._request_json(url, params)
    return do_relationship

@memoize
@sleep_after
def _request(reddit_session, page_url, params=None, url_data=None,
             openerdirector=None):
        if url_data:
            page_url += "?" + urllib.urlencode(url_data)

        # urllib2.Request throws a 404 for some reason with data=""
        encoded_params = None
        if params:
            params = dict([k, v.encode('utf-8')] for k, v in params.items())
            encoded_params = urllib.urlencode(params)
        if isinstance(page_url, unicode):
            page_url = urllib.quote(page_url.encode('utf-8'), ':/')

        request = urllib2.Request(page_url, data=encoded_params,
                                  headers=reddit_session.DEFAULT_HEADERS)
        # The openerdirector manages cookies on a per-session basis
        if openerdirector:
          response = openerdirector.open(request)
        else:
          response = urllib2.urlopen(request)
        return response.read()
