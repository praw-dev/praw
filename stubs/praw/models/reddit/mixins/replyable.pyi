from ....const import API_PATH as API_PATH
from typing import Any

class ReplyableMixin:
    def reply(self, body: Any): ...
