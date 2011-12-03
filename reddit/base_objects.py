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

from urls import urls


class RedditObject(object):
    """Base class for all Reddit API objects."""
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self)

    def __str__(self):
        raise NotImplementedError()


class RedditContentObject(RedditObject):
    """
    Base class for everything besides the Reddit class.

    Represents actual reddit objects (Comment, Redditor, etc.).
    """
    def __init__(self, reddit_session, name=None, json_dict=None, fetch=True,
                 info_url=None):
        """
        Create a new object either by name or from the dict of attributes
        returned by the API. Creating by name will retrieve the proper dict
        from the API.

        The fetch parameter specifies whether to retrieve the object's
        information from the API (only matters when it isn't provided using
        json_dict).
        """
        if name is None and json_dict is None:
            raise TypeError("Either the name or json dict is required.")

        if info_url:
            self._info_url = info_url
        else:
            self._info_url = urls["info"]
        self.reddit_session = reddit_session
        self._populate(json_dict, fetch)

    def _populate(self, json_dict, fetch):
        if json_dict is None:
            if fetch:
                json_dict = self._get_json_dict()
            else:
                json_dict = {}
        for name, value in json_dict.iteritems():
            setattr(self, name, value)
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
        if not self._populated:
            self._populate(None, True)
            return getattr(self, attr)
        raise AttributeError("'{0}' object has no attribute '{1}'".format(
                self.__class__.__name__, attr))

    def __setattr__(self, name, value):
        if name == "subreddit":
            value = Subreddit(self.reddit_session, value, fetch=False)
        elif name == "redditor" or name == "author":
            # Special case for deleted users
            if value != '[deleted]':
                value = Redditor(self.reddit_session, value, fetch=False)
        object.__setattr__(self, name, value)

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.content_id == other.content_id)

    def __ne__(self, other):
        return (type(self) != type(other) or
                self.content_id != other.content_id)

    def _get_json_dict(self):
        response = self._request_json(self._info_url, as_objects=False)
        return response["data"]

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

# These imports need to be at the end to avoid circular imports
# http://effbot.org/zone/import-confusion.htm
from redditor import Redditor
from subreddit import Subreddit
