from typing import Any, TypeVar, Generic
from typing import Dict

from .base import BaseListingMixin as BaseListingMixin
from .gilded import GildedListingMixin as GildedListingMixin
from .rising import RisingListingMixin as RisingListingMixin
from ... import ListingGenerator
from ...base import PRAWBase as PRAWBase
from ...reddit.comment import Comment
from ...reddit.subreddit import Subreddit
from ....util.cache import cachedproperty

T = TypeVar("T")

class SubredditListingMixin(BaseListingMixin, GildedListingMixin, RisingListingMixin):
    @cachedproperty
    def comments(self) -> CommentHelper[Comment]: ...
    def __init__(self, reddit: str, _data: Dict[str, Any]) -> SubredditListingMixin: ...

class CommentHelper(PRAWBase, Generic[T]):
    subreddit: Any = ...
    def __init__(self, subreddit: Subreddit) -> CommentHelper: ...
    def __call__(self, **generator_kwargs: str) -> ListingGenerator[Comment]: ...
