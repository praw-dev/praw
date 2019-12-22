from ....const import API_PATH as API_PATH
from typing import Any, Optional

class MessageableMixin:
    def message(self, subject: Any, message: Any, from_subreddit: Optional[Any] = ...) -> None: ...
