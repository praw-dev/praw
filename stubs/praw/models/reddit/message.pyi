from .base import RedditBase as RedditBase
from .mixins import FullnameMixin as FullnameMixin, InboxableMixin as InboxableMixin, ReplyableMixin as ReplyableMixin
from typing import Any
from typing import Any

from .base import RedditBase as RedditBase
from .mixins import FullnameMixin as FullnameMixin, \
    InboxableMixin as InboxableMixin, ReplyableMixin as ReplyableMixin


class Message(InboxableMixin, ReplyableMixin, FullnameMixin, RedditBase):
    STR_FIELD: str = ...
    @classmethod
    def parse(cls, data: Any, reddit: Any): ...
    def __init__(self, reddit: Any, _data: Any) -> None: ...
    def delete(self) -> None: ...

class SubredditMessage(Message):
    def mute(self, _unmute: bool = ...) -> None: ...
    def unmute(self) -> None: ...