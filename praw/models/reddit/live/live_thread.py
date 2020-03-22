"""Provide the LiveThread class."""
from typing import Any, Dict, Generator, Optional, TypeVar, Union

from ....const import API_PATH
from ....util.cache import cachedproperty
from ...listing.generator import ListingGenerator
from ..base import RedditBase
from ..mixins import FullnameMixin
from ..redditor import Redditor
from .live_contributer import LiveContributorRelationship
from .live_thread_contribution import LiveThreadContribution
from .live_update_contribution import LiveUpdateContribution

_LiveThread = TypeVar("_LiveThread")
_LiveUpdate = TypeVar("_LiveUpdate")
Reddit = TypeVar("Reddit")
Submission = TypeVar("Submission")


class LiveThread(RedditBase):
    """An individual LiveThread object.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily comprehensive.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``created_utc``         The creation time of the live thread, in `Unix
                            Time`_.
    ``description``         Description of the live thread, as Markdown.
    ``description_html``    Description of the live thread, as HTML.
    ``id``                  The ID of the live thread.
    ``nsfw``                A ``bool`` representing whether or not the live
                            thread is marked as NSFW.
    ======================= ===================================================

    .. _Unix Time: https://en.wikipedia.org/wiki/Unix_time
    """

    STR_FIELD = "id"

    @cachedproperty
    def contrib(self) -> LiveThreadContribution:
        """Provide an instance of :class:`.LiveThreadContribution`.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           thread.contrib.add('### update')

        """
        return LiveThreadContribution(self)

    @cachedproperty
    def contributor(self) -> LiveContributorRelationship:
        """Provide an instance of :class:`.LiveContributorRelationship`.

        You can call the instance to get a list of contributors which is
        represented as :class:`.RedditorList` instance consists of
        :class:`.Redditor` instances. Those Redditor instances have
        ``permissions`` attributes as contributors:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           for contributor in thread.contributor():
               # prints `(Redditor(name='Acidtwist'), [u'all'])`
               print(contributor, contributor.permissions)

        """
        return LiveContributorRelationship(self)

    def __eq__(self, other: Union[str, _LiveThread]) -> bool:
        """Return whether the other instance equals the current.

        .. note:: This comparison is case sensitive.
        """
        if isinstance(other, str):
            return other == str(self)
        return isinstance(other, self.__class__) and str(self) == str(other)

    def __getitem__(self, update_id: str) -> _LiveUpdate:
        """Return a lazy :class:`.LiveUpdate` instance.

        :param update_id: A live update ID, e.g.,
            ``'7827987a-c998-11e4-a0b9-22000b6a88d2'``.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           update = thread['7827987a-c998-11e4-a0b9-22000b6a88d2']
           update.thread     # LiveThread(id='ukaeu1ik4sw5')
           update.id         # '7827987a-c998-11e4-a0b9-22000b6a88d2'
           update.author     # 'umbrae'
        """
        return LiveUpdate(self._reddit, self.id, update_id)

    def __hash__(self) -> int:
        """Return the hash of the current instance."""
        return hash(self.__class__.__name__) ^ hash(str(self))

    def __init__(
        self,
        reddit: Reddit,
        id: Optional[str] = None,
        _data: Optional[
            Dict[str, Any]
        ] = None,  # pylint: disable=redefined-builtin
    ):
        """Initialize a lazy :class:`.LiveThread` instance.

        :param reddit: An instance of :class:`.Reddit`.
        :param id: A live thread ID, e.g., ``'ukaeu1ik4sw5'``
        """
        if bool(id) == bool(_data):
            raise TypeError("Either `id` or `_data` must be provided.")
        super().__init__(reddit, _data=_data)
        if id:
            self.id = id

    def _fetch_info(self):
        return ("liveabout", {"id": self.id}, None)

    def _fetch_data(self):
        name, fields, params = self._fetch_info()
        path = API_PATH[name].format(**fields)
        return self._reddit.request("GET", path, params)

    def _fetch(self):
        data = self._fetch_data()
        data = data["data"]
        other = type(self)(self._reddit, _data=data)
        self.__dict__.update(other.__dict__)
        self._fetched = True

    def discussions(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Generator[Submission, None, None]:
        """Get submissions linking to the thread.

        :param generator_kwargs: keyword arguments passed to
            :class:`.ListingGenerator` constructor.
        :returns: A :class:`.ListingGenerator` object which yields
            :class:`.Submission` object.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           for submission in thread.discussions(limit=None):
               print(submission.title)

        """
        url = API_PATH["live_discussions"].format(id=self.id)
        return ListingGenerator(self._reddit, url, **generator_kwargs)

    def report(self, type: str):  # pylint: disable=redefined-builtin
        """Report the thread violating the Reddit rules.

        :param type: One of ``'spam'``, ``'vote-manipulation'``,
            ``'personal-information'``, ``'sexualizing-minors'``,
            ``'site-breaking'``.

        Usage:

        .. code-block:: python

           thread = reddit.live('xyu8kmjvfrww')
           thread.report('spam')

        """
        url = API_PATH["live_report"].format(id=self.id)
        self._reddit.post(url, data={"type": type})

    def updates(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Generator[_LiveUpdate, None, None]:
        """Return a :class:`.ListingGenerator` yields :class:`.LiveUpdate` s.

        :param generator_kwargs: keyword arguments passed to
            :class:`.ListingGenerator` constructor.
        :returns: A :class:`.ListingGenerator` object which yields
            :class:`.LiveUpdate` object.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           after = 'LiveUpdate_fefb3dae-7534-11e6-b259-0ef8c7233633'
           for submission in thread.updates(limit=5, params={'after': after}):
               print(submission.body)

        """
        url = API_PATH["live_updates"].format(id=self.id)
        for update in ListingGenerator(self._reddit, url, **generator_kwargs):
            update._thread = self
            yield update


# NOTE: LiveThread and LiveUpdate call each other, so they need to be in the
# same file.


class LiveUpdate(FullnameMixin, RedditBase):
    """An individual :class:`.LiveUpdate` object.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily comprehensive.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``author``              The :class:`.Redditor` who made the update.
    ``body``                Body of the update, as Markdown.
    ``body_html``           Body of the update, as HTML.
    ``created_utc``         The time the update was created, as `Unix Time`_.
    ``stricken``            A ``bool`` representing whether or not the update
                            was stricken (see :meth:`.strike`).
    ======================= ===================================================

    .. _Unix Time: https://en.wikipedia.org/wiki/Unix_time
    """

    STR_FIELD = "id"
    _kind = "LiveUpdate"

    @cachedproperty
    def contrib(self) -> LiveUpdateContribution:
        """Provide an instance of :class:`.LiveUpdateContribution`.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           update = thread['7827987a-c998-11e4-a0b9-22000b6a88d2']
           update.contrib  # LiveUpdateContribution instance

        """
        return LiveUpdateContribution(self)

    @property
    def thread(self) -> LiveThread:
        """Return :class:`.LiveThread` object the update object belongs to."""
        return self._thread

    def __init__(
        self,
        reddit: Reddit,
        thread_id: Optional[str] = None,
        update_id: Optional[str] = None,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a lazy :class:`.LiveUpdate` instance.

        Either ``thread_id`` and ``update_id``, or ``_data`` must be
        provided.

        :param reddit: An instance of :class:`.Reddit`.
        :param thread_id: A live thread ID, e.g., ``'ukaeu1ik4sw5'``.
        :param update_id: A live update ID, e.g.,
            ``'7827987a-c998-11e4-a0b9-22000b6a88d2'``.

        Usage:

        .. code-block:: python

           update = LiveUpdate(reddit, 'ukaeu1ik4sw5',
                               '7827987a-c998-11e4-a0b9-22000b6a88d2')
           update.thread     # LiveThread(id='ukaeu1ik4sw5')
           update.id         # '7827987a-c998-11e4-a0b9-22000b6a88d2'
           update.author     # 'umbrae'
        """
        if _data is not None:
            # Since _data (part of JSON returned from reddit) have no
            # thread ID, self._thread must be set by the caller of
            # LiveUpdate(). See the code of LiveThread.updates() for example.
            super().__init__(reddit, _data=_data)
            self._fetched = True
        elif thread_id and update_id:
            super().__init__(reddit, _data=None)
            self._thread = LiveThread(self._reddit, thread_id)
            self.id = update_id
        else:
            raise TypeError(
                "Either `thread_id` and `update_id`, or "
                "`_data` must be provided."
            )

    def __setattr__(self, attribute: str, value: Any):
        """Objectify author."""
        if attribute == "author":
            value = Redditor(self._reddit, name=value)
        super().__setattr__(attribute, value)

    def _fetch(self):
        url = API_PATH["live_focus"].format(
            thread_id=self.thread.id, update_id=self.id
        )
        other = self._reddit.get(url)[0]
        self.__dict__.update(other.__dict__)
        self._fetched = True
