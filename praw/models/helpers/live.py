"""Container for LiveHelper."""
from typing import Generator, List, Optional

from ...const import API_PATH
from ..base import PRAWBase
from ..reddit.live import LiveThread


class LiveHelper(PRAWBase):
    """Provide a set of functions to interact with LiveThreads."""

    def __call__(
        self, id: str
    ) -> LiveThread:  # pylint: disable=invalid-name,redefined-builtin
        """Return a new lazy instance of :class:`~.LiveThread`.

        This method is intended to be used as:

        .. code-block:: python

            livethread = reddit.live('ukaeu1ik4sw5')

        :param id: A live thread ID, e.g., ``ukaeu1ik4sw5``.
        """
        return LiveThread(self._reddit, id=id)

    def info(self, ids: List[str]) -> Generator[LiveThread, None, None]:
        """Fetch information about each live thread in ``ids``.

        :param ids: A list of IDs for a live thread.
        :returns: A generator that yields :class:`.LiveThread` instances.

        Live threads that cannot be matched will not be generated.
        Requests will be issued in batches for each 100 IDs.

        .. note::
            This method doesn't support IDs for live updates.

        .. warning:
            Unlike :meth:`.Reddit.info`, the output of this method
            may not reflect the order of input.

        Usage:

        .. code-block:: python

            ids = ['3rgnbke2rai6hen7ciytwcxadi',
                   'sw7bubeycai6hey4ciytwamw3a',
                   't8jnufucss07']
            for thread in reddit.live.info(ids)
                print(thread.title)

        """
        if not isinstance(ids, list):
            raise TypeError("ids must be a list")

        def generator():
            for position in range(0, len(ids), 100):
                ids_chunk = ids[position : position + 100]
                url = API_PATH["live_info"].format(ids=",".join(ids_chunk))
                params = {"limit": 100}  # 25 is used if not specified
                for result in self._reddit.get(url, params=params):
                    yield result

        return generator()

    def create(
        self,
        title: str,
        description: Optional[str] = None,
        nsfw: bool = False,
        resources: str = None,
    ) -> LiveThread:
        """Create a new LiveThread.

        :param title: The title of the new LiveThread.
        :param description: (Optional) The new LiveThread's description.
        :param nsfw: (boolean) Indicate whether this thread is not safe for
            work (default: False).
        :param resources: (Optional) Markdown formatted information that is
            useful for the LiveThread.
        :returns: The new LiveThread object.

        """
        return self._reddit.post(
            API_PATH["livecreate"],
            data={
                "description": description,
                "nsfw": nsfw,
                "resources": resources,
                "title": title,
            },
        )

    def now(self) -> Optional[LiveThread]:
        """Get the currently featured live thread.

        :returns: The :class:`.LiveThread` object, or ``None`` if there is
            no currently featured live thread.

        Usage:

        .. code-block:: python

        thread = reddit.live.now()  # LiveThread object or None

        """
        return self._reddit.get(API_PATH["live_now"])
