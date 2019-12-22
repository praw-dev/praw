from ....const import API_PATH as API_PATH
from typing import Any

class ReportableMixin:
    def report(self, reason: Any) -> None: ...
