"""Provides the Objector class."""

from json import loads
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from .exceptions import ClientException, RedditAPIException
from .models.reddit.base import RedditBase
from .util import snake_case_keys

if TYPE_CHECKING:  # pragma: no cover
    from .. import Reddit


class Objector:
    """The objector builds :class:`.RedditBase` objects."""

    @classmethod
    def parse_error(
        cls, data: Union[List[Any], Dict[str, Dict[str, str]]]
    ) -> Optional[RedditAPIException]:
        """Convert JSON response into an error object.

        :param data: The dict to be converted.
        :returns: An instance of :class:`~.RedditAPIException`, or ``None`` if ``data``
            doesn't fit this model.

        """
        if isinstance(data, list):
            # Fetching a Submission returns a list (of two items). Although it's handled
            # manually in `Submission._fetch()`, assume it's a possibility here.
            return None

        errors = data.get("json", {}).get("errors")
        if errors is None:
            return None
        if len(errors) < 1:
            # See `Collection._fetch()`.
            raise ClientException("successful error response", data)
        return RedditAPIException(errors)

    @classmethod
    def check_error(cls, data: Union[List[Any], Dict[str, Dict[str, str]]]):
        """Raise an error if the argument resolves to an error object."""
        error = cls.parse_error(data)
        if error:
            raise error

    def __init__(self, reddit: "Reddit", parsers: Optional[Dict[str, Any]] = None):
        """Initialize an Objector instance.

        :param reddit: An instance of :class:`~.Reddit`.

        """
        self.parsers = {} if parsers is None else parsers
        self._reddit = reddit

    def _objectify_dict(self, data):
        """Create RedditBase objects from dicts.

        :param data: The structured data, assumed to be a dict.
        :returns: An instance of :class:`~.RedditBase`.

        """
        if {"conversation", "messages", "modActions"}.issubset(data):
            parser = self.parsers["ModmailConversation"]
        elif {"actionTypeId", "author", "date"}.issubset(data):
            # Modmail mod action
            data = snake_case_keys(data)
            parser = self.parsers["ModmailAction"]
        elif {"bodyMarkdown", "isInternal"}.issubset(data):
            # Modmail message
            data = snake_case_keys(data)
            parser = self.parsers["ModmailMessage"]
        elif {"kind", "short_name", "violation_reason"}.issubset(data):
            # This is a Rule
            parser = self.parsers["rule"]
        elif {"isAdmin", "isDeleted"}.issubset(data):
            # Modmail author
            data = snake_case_keys(data)
            # Prevent clobbering base-36 id
            del data["id"]
            data["is_subreddit_mod"] = data.pop("is_mod")
            parser = self.parsers[self._reddit.config.kinds["redditor"]]
        elif {"banStatus", "muteStatus", "recentComments"}.issubset(data):
            # Modmail user
            data = snake_case_keys(data)
            data["created_string"] = data.pop("created")
            parser = self.parsers[self._reddit.config.kinds["redditor"]]
        elif {"displayName", "id", "type"}.issubset(data):
            # Modmail subreddit
            data = snake_case_keys(data)
            parser = self.parsers[self._reddit.config.kinds[data["type"]]]
        elif {"date", "id", "name"}.issubset(data) or {
            "id",
            "name",
            "permissions",
        }.issubset(data):
            parser = self.parsers[self._reddit.config.kinds["redditor"]]
        elif {"text", "url"}.issubset(data):
            if "color" in data or "linkUrl" in data:
                parser = self.parsers["Button"]
            else:
                parser = self.parsers["MenuLink"]
        elif {"children", "text"}.issubset(data):
            parser = self.parsers["Submenu"]
        elif {"height", "url", "width"}.issubset(data):
            parser = self.parsers["Image"]
        elif {"isSubscribed", "name", "subscribers"}.issubset(data):
            # discards icon and subscribed information
            return self._reddit.subreddit(data["name"])
        elif {"authorFlairType", "name"}.issubset(data):
            # discards flair information
            return self._reddit.redditor(data["name"])
        elif {"parent_id"}.issubset(data):
            parser = self.parsers[self._reddit.config.kinds["comment"]]
        elif "collection_id" in data.keys():
            parser = self.parsers["Collection"]
        elif {"moderators", "moderatorIds", "allUsersLoaded", "subredditId"}.issubset(
            data
        ):
            data = snake_case_keys(data)
            moderators = []
            for mod_id in data["moderator_ids"]:
                mod = snake_case_keys(data["moderators"][mod_id])
                mod["mod_permissions"] = list(mod["mod_permissions"].keys())
                moderators.append(mod)
            data["moderators"] = moderators
            parser = self.parsers["moderator-list"]
        elif "username" in data.keys():
            data["name"] = data.pop("username")
            parser = self.parsers[self._reddit.config.kinds["redditor"]]
        else:
            if "user" in data:
                parser = self.parsers[self._reddit.config.kinds["redditor"]]
                data["user"] = parser.parse({"name": data["user"]}, self._reddit)
            return data
        return parser.parse(data, self._reddit)

    def objectify(
        self, data: Optional[Union[Dict[str, Any], List[Any]]]
    ) -> Optional[Union[RedditBase, Dict[str, Any], List[Any]]]:
        """Create RedditBase objects from data.

        :param data: The structured data.
        :returns: An instance of :class:`~.RedditBase`, or ``None`` if given ``data`` is
            ``None``.

        """
        # pylint: disable=too-many-return-statements
        if data is None:  # 204 no content
            return None
        if isinstance(data, list):
            return [self.objectify(item) for item in data]
        if "json" in data and "errors" in data["json"]:
            errors = data["json"]["errors"]
            if len(errors) > 0:
                raise RedditAPIException(errors)
        if "kind" in data and (
            "shortName" in data or data["kind"] in ("menu", "moderators")
        ):
            # This is a widget
            parser = self.parsers.get(data["kind"], self.parsers["widget"])
            return parser.parse(data, self._reddit)
        if {"kind", "data"}.issubset(data) and data["kind"] in self.parsers:
            parser = self.parsers[data["kind"]]
            return parser.parse(data["data"], self._reddit)
        if "json" in data and "data" in data["json"]:
            if "websocket_url" in data["json"]["data"]:
                return data
            if "things" in data["json"]["data"]:  # Submission.reply
                return self.objectify(data["json"]["data"]["things"])
            if "rules" in data["json"]["data"]:
                return self.objectify(loads(data["json"]["data"]["rules"]))
            if "url" in data["json"]["data"]:  # Subreddit.submit
                # The URL is the URL to the submission, so it's removed.
                del data["json"]["data"]["url"]
                parser = self.parsers[self._reddit.config.kinds["submission"]]
                if data["json"]["data"]["id"].startswith(
                    f"{self._reddit.config.kinds['submission']}_"
                ):
                    # With polls, Reddit returns a fullname but calls it an "id". This
                    # fixes this by coercing the fullname into an id.
                    data["json"]["data"]["id"] = data["json"]["data"]["id"].split(
                        "_", 1
                    )[1]
            else:
                parser = self.parsers["LiveUpdateEvent"]
            return parser.parse(data["json"]["data"], self._reddit)
        if "rules" in data:
            return self.objectify(data["rules"])
        elif isinstance(data, dict):
            return self._objectify_dict(data)

        return data
