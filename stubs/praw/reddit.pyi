from typing import (
    Any,
    Optional,
    NoReturn,
    Dict,
    Union,
    Sequence,
    Generator,
    IO,
)

from prawcore import Requestor

from .config import Config as Config
from .models import (
    Auth,
    Front,
    Inbox,
    LiveHelper,
    MultiredditHelper,
    Redditors,
    SubredditHelper,
    Subreddits,
)
from .models import (
    User,
    Comment,
    Subreddit,
    Redditor,
    DomainListing,
    Submission,
)
from .models.reddit.base import RedditBase

UPDATE_CHECKER_MISSING: bool

class Reddit:
    update_checked: bool = ...
    @property
    def read_only(self) -> bool: ...
    @read_only.setter
    def read_only(self, value: bool) -> NoReturn: ...
    def __enter__(self): ...
    def __exit__(self, *_args: Any) -> NoReturn: ...
    config: Config = ...
    auth: Auth = ...
    front: Front = ...
    inbox: Inbox = ...
    live: LiveHelper = ...
    multireddit: MultiredditHelper = ...
    redditors: Redditors = ...
    subreddit: SubredditHelper = ...
    subreddits: Subreddits = ...
    user: User = ...
    def __init__(
        self,
        site_name: Optional[str] = ...,
        requestor_class: Optional[Requestor] = ...,
        requestor_kwargs: Optional[Dict[str, Union[str, Any]]] = ...,
        **config_settings: Any
    ) -> None: ...
    def comment(
        self, id: Optional[str] = ..., url: Optional[str] = ...
    ) -> Comment: ...
    def domain(self, domain: str) -> DomainListing: ...
    def get(
        self, path: str, params: Optional[Union[Dict[str, str], str]] = ...
    ) -> Optional[RedditBase]: ...
    def info(
        self,
        fullnames: Optional[
            Sequence[Union[Comment, Subreddit, Submission]]
        ] = ...,
        url: Optional[str] = ...,
    ) -> Generator[Any]: ...
    def patch(
        self,
        path: str,
        data: Optional[
            Union[Dict[str, Union[str, Any]], bytes, IO, str]
        ] = ...,
    ) -> Optional[RedditBase]: ...
    def post(
        self,
        path: str,
        data: Optional[
            Union[Dict[str, Union[str, Any]], bytes, IO, str]
        ] = ...,
        files: Optional[Dict[str, IO]] = ...,
        params: Optional[Union[str, Dict[str, str]]] = ...,
    ) -> Optional[RedditBase]: ...
    def put(
        self,
        path: str,
        data: Optional[
            Union[Dict[str, Union[str, Any]], bytes, IO, str]
        ] = ...,
    ) -> Optional[RedditBase]: ...
    def random_subreddit(self, nsfw: bool = ...) -> Subreddit: ...
    def redditor(
        self, name: Optional[str] = ..., fullname: Optional[str] = ...
    ) -> Redditor: ...
    def request(
        self,
        method: str,
        path: str,
        params: Optional[Union[str, Dict[str, str]]] = ...,
        data: Optional[
            Union[Dict[str, Union[str, Any]], bytes, IO, str]
        ] = ...,
        files: Optional[Dict[str, IO]] = ...,
    ) -> Optional[RedditBase]: ...
    def submission(
        self, id: Optional[str] = ..., url: Optional[str] = ...
    ) -> Submission: ...
