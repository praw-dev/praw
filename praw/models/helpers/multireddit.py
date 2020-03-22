"""Container for MultiredditHelper."""
from json import dumps
from typing import Optional, Union

from ...const import API_PATH
from ..base import PRAWBase
from ..reddit.multi import Multireddit, Subreddit
from ..reddit.redditor import Redditor


class MultiredditHelper(PRAWBase):
    """Provide a set of functions to interact with Multireddits."""

    def __call__(
        self, redditor: Union[str, Redditor], name: str
    ) -> Multireddit:
        """Return a lazy instance of :class:`~.Multireddit`.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance who owns the multireddit.
        :param name: The name of the multireddit.

        """
        path = "/user/{}/m/{}".format(redditor, name)
        return Multireddit(self._reddit, _data={"name": name, "path": path})

    def create(
        self,
        display_name: str,
        subreddits: Union[str, Subreddit],
        description_md: Optional[str] = None,
        icon_name: Optional[str] = None,
        key_color: Optional[str] = None,
        visibility: str = "private",
        weighting_scheme: str = "classic",
    ) -> Multireddit:
        """Create a new multireddit.

        :param display_name: The display name for the new multireddit.
        :param subreddits: Subreddits to add to the new multireddit.
        :param description_md: (Optional) Description for the new multireddit,
            formatted in markdown.
        :param icon_name: (Optional) Can be one of: ``art
            and design``, ``ask``, ``books``, ``business``, ``cars``,
            ``comics``, ``cute animals``, ``diy``, ``entertainment``, ``food
            and drink``, ``funny``, ``games``, ``grooming``, ``health``, ``life
            advice``, ``military``, ``models pinup``, ``music``, ``news``,
            ``philosophy``, ``pictures and gifs``, ``science``, ``shopping``,
            ``sports``, ``style``, ``tech``, ``travel``, ``unusual stories``,
            ``video``, or ``None``.
        :param key_color: (Optional) RGB hex color code of the form
            ``'#FFFFFF'``.
        :param visibility: (Optional) Can be one of: ``hidden``, ``private``,
            ``public`` (default: private).
        :param weighting_scheme: (Optional) Can be one of: ``classic``,
            ``fresh`` (default: classic).
        :returns: The new Multireddit object.

        """
        model = {
            "description_md": description_md,
            "display_name": display_name,
            "icon_name": icon_name,
            "key_color": key_color,
            "subreddits": [{"name": str(sub)} for sub in subreddits],
            "visibility": visibility,
            "weighting_scheme": weighting_scheme,
        }
        return self._reddit.post(
            API_PATH["multireddit_base"], data={"model": dumps(model)}
        )
