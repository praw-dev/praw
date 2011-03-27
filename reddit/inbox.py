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
      return [msg for msg in self.messages if msg.new]
