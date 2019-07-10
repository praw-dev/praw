"""Provides the Objector class."""
from . import models
from .exceptions import APIException
from .util import snake_case_keys


class Objector:
    """The objector builds :class:`.RedditBase` objects."""

    @classmethod
    def parse_error(cls, data):
        """Convert JSON response into an error object.

        :param data: The dict to be converted.
        :returns: An instance of :class:`~.APIException`, or ``None`` if
            ``data`` doesn't fit this model.

        """
        errors = data.get("json", {}).get("errors", ())
        if not errors:
            return None
        if len(errors) > 1:
            # TODO
            raise AssertionError(
                "multiple error descriptions in response", data
            )
        return APIException(*errors[0])

    @classmethod
    def check_error(cls, data):
        """Raise an error if the argument resolves to an error object."""
        error = cls.parse_error(data)
        if error:
            raise error

    def __init__(self, reddit):
        """Initialize an Objector instance.

        :param reddit: An instance of :class:`~.Reddit`.

        """
        self.parsers = {
            reddit.config.kinds["comment"]: models.Comment,
            reddit.config.kinds["message"]: models.Message,
            reddit.config.kinds["redditor"]: models.Redditor,
            reddit.config.kinds["submission"]: models.Submission,
            reddit.config.kinds["subreddit"]: models.Subreddit,
            reddit.config.kinds["trophy"]: models.Trophy,
            "Button": models.Button,
            "Collection": models.Collection,
            "Image": models.Image,
            "LabeledMulti": models.Multireddit,
            "Listing": models.Listing,
            "LiveUpdate": models.LiveUpdate,
            "LiveUpdateEvent": models.LiveThread,
            "MenuLink": models.MenuLink,
            "ModmailAction": models.ModmailAction,
            "ModmailConversation": models.ModmailConversation,
            "ModmailMessage": models.ModmailMessage,
            "Submenu": models.Submenu,
            "TrophyList": models.TrophyList,
            "UserList": models.RedditorList,
            "button": models.ButtonWidget,
            "calendar": models.Calendar,
            "community-list": models.CommunityList,
            "custom": models.CustomWidget,
            "id-card": models.IDCard,
            "image": models.ImageWidget,
            "menu": models.Menu,
            "modaction": models.ModAction,
            "moderators": models.ModeratorsWidget,
            "more": models.MoreComments,
            "post-flair": models.PostFlairWidget,
            "stylesheet": models.Stylesheet,
            "subreddit-rules": models.RulesWidget,
            "textarea": models.TextArea,
            "widget": models.Widget,
        }
        self._reddit = reddit

    def _objectify_dict(self, data):  # pragma: no cover
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
        else:
            if "user" in data:
                parser = self.parsers[self._reddit.config.kinds["redditor"]]
                data["user"] = parser.parse(
                    {"name": data["user"]}, self._reddit
                )
            return data
        return parser.parse(data, self._reddit)

    def objectify(self, data):  # pragma: no cover
        """Create RedditBase objects from data.

        :param data: The structured data.
        :returns: An instance of :class:`~.RedditBase`, or ``None`` if
            given ``data`` is ``None``.

        """
        # pylint: disable=too-many-return-statements
        if data is None:  # 204 no content
            return None
        if isinstance(data, list):
            return [self.objectify(item) for item in data]
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
            if "url" in data["json"]["data"]:  # Subreddit.submit
                # The URL is the URL to the submission, so it's removed.
                del data["json"]["data"]["url"]
                parser = self.parsers[self._reddit.config.kinds["submission"]]
            else:
                parser = self.parsers["LiveUpdateEvent"]
            return parser.parse(data["json"]["data"], self._reddit)
        if "json" in data and "errors" in data["json"]:
            errors = data["json"]["errors"]
            if len(errors) == 1:
                raise APIException(*errors[0])
            assert not errors
        elif isinstance(data, dict):
            return self._objectify_dict(data)

        return data
