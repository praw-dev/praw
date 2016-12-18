"""Provide the LiveThread class."""
from ...const import API_PATH
from ..listing.generator import ListingGenerator
from .base import RedditBase
from .redditor import Redditor


class LiveThread(RedditBase):
    """An individual LiveThread object."""

    STR_FIELD = 'id'

    def __eq__(self, other):
        """Return whether the other instance equals the current.

        .. note:: This comparison is case sensitive.
        """
        if isinstance(other, str):
            return other == str(self)
        return (isinstance(other, self.__class__) and
                str(self) == str(other))

    def __getitem__(self, update_id):
        """Return a lazy :class:`.LiveUpdate` instance.

        .. warning:: At this time, accesing lazy attributes, whose value
           have not loaded, raises ``AttributeError``.

        :param update_id: A live update ID, e.g.,
            ``'7827987a-c998-11e4-a0b9-22000b6a88d2'``.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           update = thread['7827987a-c998-11e4-a0b9-22000b6a88d2']
           update.thread     # LiveThread(id='ukaeu1ik4sw5')
           update.id         # '7827987a-c998-11e4-a0b9-22000b6a88d2'
           update.author     # raise ``AttributeError``
        """
        return LiveUpdate(self._reddit, self.id, update_id)

    def __hash__(self):
        """Return the hash of the current instance."""
        return hash(self.__class__.__name__) ^ hash(str(self))

    def __init__(self, reddit, id=None,  # pylint: disable=redefined-builtin
                 _data=None):
        """Initialize a lazy :class:`.LiveThread` instance.

        :param reddit: An instance of :class:`.Reddit`.
        :param id: A live thread ID, e.g., ``'ukaeu1ik4sw5'``
        """
        if bool(id) == bool(_data):
            raise TypeError('Either `id` or `_data` must be provided.')
        super(LiveThread, self).__init__(reddit, _data)
        if id:
            self.id = id  # pylint: disable=invalid-name

    def _info_path(self):
        return API_PATH['liveabout'].format(id=self.id)

    def updates(self, **generator_kwargs):
        """Return a :class:`.ListingGenerator` yields :class:`.LiveUpdate` s.

        :param generator_kwargs: keyword arguments passed to
            :class:`.ListingGenerator` constructor.
        :returns: A :class:`.ListingGenerator` object which yields
            :class:`.LiveUpdate` object.
        """
        url = API_PATH['live_updates'].format(id=self.id)
        for update in ListingGenerator(self._reddit, url,
                                       **generator_kwargs):
            update._thread = self
            yield update


class LiveUpdate(RedditBase):
    """An individual :class:`.LiveUpdate` object."""

    STR_FIELD = 'id'

    @property
    def thread(self):
        """Return :class:`.LiveThread` object the update object belongs to."""
        return self._thread

    def __init__(self, reddit, thread_id=None, update_id=None, _data=None):
        """Initialize a lazy :class:`.LiveUpdate` instance.

        Either ``thread_id`` and ``update_id``, or ``_data`` must be
        provided.

        .. warning:: At this time, accesing lazy attributes, whose value
           have not loaded, raises ``AttributeError``.

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
           update.author     # raise ``AttributeError``
        """
        if _data is not None:
            super(LiveUpdate, self).__init__(reddit, _data)
            self._fetched = True
        elif thread_id and update_id:
            super(LiveUpdate, self).__init__(reddit, None)
            self._thread = LiveThread(self._reddit, thread_id)
            self.id = update_id  # pylint: disable=invalid-name
            self._fetched = True
        else:
            raise TypeError('Either `thread_id` and `update_id`, or '
                            '`_data` must be provided.')

    def __setattr__(self, attribute, value):
        """Objectify author."""
        if attribute == 'author':
            value = Redditor(self._reddit, name=value)
        super(LiveUpdate, self).__setattr__(attribute, value)
