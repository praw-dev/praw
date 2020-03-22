"""Provide the SubmissionFlair class."""
from typing import Dict, List, Optional, TypeVar, Union

from ....const import API_PATH

_Submission = TypeVar("_Submission")


class SubmissionFlair:
    """Provide a set of functions pertaining to Submission flair."""

    def __init__(self, submission: _Submission):
        """Create a SubmissionFlair instance.

        :param submission: The submission associated with the flair functions.

        """
        self.submission = submission

    def choices(self) -> List[Dict[str, Union[bool, list, str]]]:
        """Return list of available flair choices.

        Choices are required in order to use :meth:`.select`.

        For example:

        .. code-block:: python

           choices = submission.flair.choices()

        """
        url = API_PATH["flairselector"].format(
            subreddit=self.submission.subreddit
        )
        return self.submission._reddit.post(
            url, data={"link": self.submission.fullname}
        )["choices"]

    def select(self, flair_template_id: str, text: Optional[str] = None):
        """Select flair for submission.

        :param flair_template_id: The flair template to select. The possible
            ``flair_template_id`` values can be discovered through
            :meth:`.choices`.
        :param text: If the template's ``flair_text_editable`` value is True,
            this value will set a custom text (default: None).

        For example, to select an arbitrary editable flair text (assuming there
        is one) and set a custom value try:

        .. code-block:: python

           choices = submission.flair.choices()
           template_id = next(x for x in choices
                              if x['flair_text_editable'])['flair_template_id']
           submission.flair.select(template_id, 'my custom value')

        """
        data = {
            "flair_template_id": flair_template_id,
            "link": self.submission.fullname,
            "text": text,
        }
        url = API_PATH["select_flair"].format(
            subreddit=self.submission.subreddit
        )
        self.submission._reddit.post(url, data=data)
