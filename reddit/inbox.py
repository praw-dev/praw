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

from base_objects import RedditContentObject
from urls import urls

class Inbox(RedditContentObject):
    """A class for reading messages."""

    kind = "t1"

    def __init__(self, reddit_session, json_dict=None, fetch=True):
      self.URL = urls["inbox"]
      self.messages = None
      super(Inbox, self).__init__(reddit_session, "Inbox", json_dict, fetch)

    def get_messages(self, force = False, *args, **kwargs):
      # Crude caching
      if self.messages == None or force:
        self.messages = self._request_json(self.URL)["data"]["children"]
      return self.messages

    def get_new_messages(self):
      self.get_messages(force = True)
      return [msg for msg in self.messages if hasattr(msg, "new") and msg.new]
      
    def __str__(self):
      if self.messages == None:
        return "<Inbox: No messages>"
      return "<Inbox: %d messages>" % len(self.messages)
