"""Provide the LiveThread class."""
from ...const import API_PATH
from ..listing.generator import ListingGenerator
from ..list.redditor import RedditorList
from .base import RedditBase
from .redditor import Redditor


class LiveContributorRelationship(object):
    """Provide methods to interact with live threads' contributors."""

    @staticmethod
    def _handle_permissions(permissions):
        if permissions is None:
            permissions = {'all'}
        else:
            permissions = set(permissions)
        return ','.join('+{}'.format(x) for x in permissions)

    def __call__(self):
        """Return a :class:`.RedditorList` for live threads' contributors.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           for contributor in thread.contributor():
               print(contributor)

        """
        url = API_PATH['live_contributors'].format(id=self.thread.id)
        temp = self.thread._reddit.get(url)
        return temp if isinstance(temp, RedditorList) else temp[0]

    def __init__(self, thread):
        """Create a :class:`.LiveContributorRelationship` instance.

        :param thread: An instance of :class:`.LiveThread`.

        .. note:: This class should not be initialized directly. Instead obtain
           an instance via: ``thread.contributor`` where ``thread`` is a
           :class:`.LiveThread` instance.

        """
        self.thread = thread

    def accept_invite(self):
        """Accept an invite to contribute the live thread.

        Usage:

        .. code-block:: python

            thread = reddit.live('ydwwxneu7vsa')
            thread.contributor.accept_invite()

        """
        url = API_PATH['live_accept_invite'].format(id=self.thread.id)
        self.thread._reddit.post(url)

    def invite(self, redditor, permissions=None):
        """Invite a redditor to be a contributor of the live thread.

        Raise :class:`praw.exceptions.APIException` if the invitation
        already exists.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should
            be a list of strings specifying which subset of permissions to
            grant. An empty list ``[]`` indicates no permissions, and when
            not provided (``None``), indicates full permissions.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           redditor = reddit.redditor('spez')

           # 'manage' and 'settings' permissions
           thread.contributor.invite(redditor, ['manage', 'settings'])

        :seealso: :meth:`.LiveContributorRelationship.remove_invite` to
            remove the invite for redditor.

        """
        url = API_PATH['live_invite'].format(id=self.thread.id)
        data = {'name': str(redditor),
                'type': 'liveupdate_contributor_invite',
                'permissions': self._handle_permissions(permissions)}
        self.thread._reddit.post(url, data=data)

    def leave(self):
        """Abdicate the live thread contributor position (use with care).

        Usage:

        .. code-block:: python

            thread = reddit.live('ydwwxneu7vsa')
            thread.contributor.leave()

        """
        url = API_PATH['live_leave'].format(id=self.thread.id)
        self.thread._reddit.post(url)

    def remove(self, redditor):
        """Remove the redditor from the live thread contributors.

        :param redditor: A redditor fullname (e.g., ``'t2_1w72'``) or
            :class:`~.Redditor` instance.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           redditor = reddit.redditor('spez')
           thread.contributor.remove(redditor)
           thread.contributor.remove('t2_1w72')  # with fullname

        """
        if isinstance(redditor, Redditor):
            fullname = redditor.fullname
        else:
            fullname = redditor
        data = {'id': fullname}
        url = API_PATH['live_remove_contrib'].format(id=self.thread.id)
        self.thread._reddit.post(url, data=data)

    def remove_invite(self, redditor):
        """Remove the invite for redditor.

        :param redditor: A redditor fullname (e.g., ``'t2_1w72'``) or
            :class:`~.Redditor` instance.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           redditor = reddit.redditor('spez')
           thread.contributor.remove_invite(redditor)
           thread.contributor.remove_invite('t2_1w72')  # with fullname

        :seealso: :meth:`.LiveContributorRelationship.invite` to
            invite a redditor to be a contributor of the live thread.

        """
        if isinstance(redditor, Redditor):
            fullname = redditor.fullname
        else:
            fullname = redditor
        data = {'id': fullname}
        url = API_PATH['live_remove_invite'].format(id=self.thread.id)
        self.thread._reddit.post(url, data=data)

    def update(self, redditor, permissions=None):
        """Update the contributor permissions for ``redditor``.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should
            be a list of strings specifying which subset of permissions to
            grant (other permissions are removed). An empty list ``[]``
            indicates no permissions, and when not provided (``None``),
            indicates full permissions.

        For example, to grant all permissions to the contributor, try:

        .. code:: python

           thread = reddit.live('ukaeu1ik4sw5')
           thread.contributor.update('spez')

        To grant 'access' and 'edit' permissions (and to remove other
        permissions), try:

        .. code:: python

           thread.contributor.update('spez', ['access', 'edit'])

        To remove all permissions from the contributor, try:

        .. code:: python

           subreddit.moderator.update('spez', [])

        """
        url = API_PATH['live_update_perms'].format(id=self.thread.id)
        data = {'name': str(redditor),
                'type': 'liveupdate_contributor',
                'permissions': self._handle_permissions(permissions)}
        self.thread._reddit.post(url, data=data)

    def update_invite(self, redditor, permissions=None):
        """Update the contributor invite permissions for ``redditor``.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should
            be a list of strings specifying which subset of permissions to
            grant (other permissions are removed). An empty list ``[]``
            indicates no permissions, and when not provided (``None``),
            indicates full permissions.

        For example, to set all permissions to the invitation, try:

        .. code:: python

           thread = reddit.live('ukaeu1ik4sw5')
           thread.contributor.update_invite('spez')

        To set 'access' and 'edit' permissions (and to remove other
        permissions) to the invitation, try:

        .. code:: python

           thread.contributor.update_invite('spez', ['access', 'edit'])

        To remove all permissions from the invitation, try:

        .. code:: python

           thread.contributor.update_invite('spez', [])

        """
        url = API_PATH['live_update_perms'].format(id=self.thread.id)
        data = {'name': str(redditor),
                'type': 'liveupdate_contributor_invite',
                'permissions': self._handle_permissions(permissions)}
        self.thread._reddit.post(url, data=data)


class LiveThread(RedditBase):
    """An individual LiveThread object."""

    STR_FIELD = 'id'

    @property
    def contrib(self):
        """Provide an instance of :class:`.LiveThreadContribution`.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           thread.contrib.add('### update')

        """
        if self._contrib is None:
            self._contrib = LiveThreadContribution(self)
        return self._contrib

    @property
    def contributor(self):
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
        if self._contributor is None:
            self._contributor = LiveContributorRelationship(self)
        return self._contributor

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
        self._contrib = None
        self._contributor = None

    def _info_path(self):
        return API_PATH['liveabout'].format(id=self.id)

    def discussions(self, **generator_kwargs):
        """Get submissions linking to the thread.

        :param generator_kwargs: keyword arguments passed to
            :class:`.ListingGenerator` constructor.
        :returns: A :class:`.ListingGenerator` object which yields
            :class:`.Submission` object.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           for submission in thread.discussions(limit=None):
               print(submission.title)

        """
        url = API_PATH['live_discussions'].format(id=self.id)
        return ListingGenerator(self._reddit, url, **generator_kwargs)

    def report(self, type):  # pylint: disable=redefined-builtin
        """Report the thread violating the Reddit rules.

        :param type: One of ``'spam'``, ``'vote-manipulation'``,
            ``'personal-information'``, ``'sexualizing-minors'``,
            ``'site-breaking'``.

        Usage:

        .. code-block:: python

           thread = reddit.live('xyu8kmjvfrww')
           thread.report('spam')

        """
        url = API_PATH['live_report'].format(id=self.id)
        self._reddit.post(url, data={'type': type})

    def updates(self, **generator_kwargs):
        """Return a :class:`.ListingGenerator` yields :class:`.LiveUpdate` s.

        :param generator_kwargs: keyword arguments passed to
            :class:`.ListingGenerator` constructor.
        :returns: A :class:`.ListingGenerator` object which yields
            :class:`.LiveUpdate` object.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           after = 'LiveUpdate_fefb3dae-7534-11e6-b259-0ef8c7233633'
           for submission in thread.updates(limit=5, params={'after': after}):
               print(submission.body)

        """
        url = API_PATH['live_updates'].format(id=self.id)
        for update in ListingGenerator(self._reddit, url,
                                       **generator_kwargs):
            update._thread = self
            yield update


class LiveThreadContribution(object):
    """Provides a set of contribution functions to a LiveThread."""

    def __init__(self, thread):
        """Create an instance of :class:`.LiveThreadContribution`.

        :param thread: An instance of :class:`.LiveThread`.

        This instance can be retrieved through ``thread.contrib``
        where thread is a :class:`.LiveThread` instance. E.g.,

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           thread.contrib.add('### update')

        """
        self.thread = thread

    def add(self, body):
        """Add an update to the live thread.

        :param body: The markdown formatted content for the update.

        Usage:

        .. code-block:: python

           thread = reddit.live('ydwwxneu7vsa')
           thread.contrib.add('test `LiveThreadContribution.add()`')

        """
        url = API_PATH['live_add_update'].format(id=self.thread.id)
        self.thread._reddit.post(url, data={'body': body})

    def close(self):
        """Close the live thread permanently (cannot be undone).

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           thread.contrib.close()

        """
        url = API_PATH['live_close'].format(id=self.thread.id)
        self.thread._reddit.post(url)

    def update(self, title=None, description=None, nsfw=None, resources=None,
               **other_settings):
        """Update settings of the live thread.

        :param title: (Optional) The title of the live thread (default: None).
        :param description: (Optional) The live thread's description
            (default: None).
        :param nsfw: (Optional) Indicate whether this thread is not safe for
            work (default: None).
        :param resources: (Optional) Markdown formatted information that is
            useful for the live thread (default: None).

        Does nothing if no arguments are provided.

        Each setting will maintain its current value if ``None`` is specified.

        Additional keyword arguments can be provided to handle new settings as
        Reddit introduces them.

        Usage:

        .. code-block:: python

           thread = reddit.live('xyu8kmjvfrww')

           # update `title` and `nsfw`
           updated_thread = thread.contrib.update(title=new_title, nsfw=True)

        If Reddit introduces new settings, you must specify ``None`` for the
        setting you want to maintain:

        .. code-block:: python

           # update `nsfw` and maintain new setting `foo`
           thread.contrib.update(nsfw=True, foo=None)

        """
        settings = {'title': title, 'description': description,
                    'nsfw': nsfw, 'resources': resources}
        settings.update(other_settings)
        if all(value is None for value in settings.values()):
            return
        # get settings from Reddit (not cache)
        thread = LiveThread(self.thread._reddit, self.thread.id)
        data = {key: getattr(thread, key) if value is None else value
                for key, value in settings.items()}

        url = API_PATH['live_update_thread'].format(id=self.thread.id)
        # prawcore (0.7.0) Session.request() modifies `data` kwarg
        self.thread._reddit.post(url, data=data.copy())
        self.thread._reset_attributes(*data.keys())


class LiveUpdate(RedditBase):
    """An individual :class:`.LiveUpdate` object."""

    STR_FIELD = 'id'

    @property
    def contrib(self):
        """Provide an instance of :class:`.LiveUpdateContribution`.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           update = thread['7827987a-c998-11e4-a0b9-22000b6a88d2']
           update.contrib  # LiveUpdateContribution instance

        """
        if self._contrib is None:
            self._contrib = LiveUpdateContribution(self)
        return self._contrib

    @property
    def thread(self):
        """Return :class:`.LiveThread` object the update object belongs to."""
        return self._thread

    def __init__(self, reddit, thread_id=None, update_id=None, _data=None):
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
            super(LiveUpdate, self).__init__(reddit, _data)
            self._fetched = True
        elif thread_id and update_id:
            super(LiveUpdate, self).__init__(reddit, None)
            self._thread = LiveThread(self._reddit, thread_id)
            self.id = update_id  # pylint: disable=invalid-name
        else:
            raise TypeError('Either `thread_id` and `update_id`, or '
                            '`_data` must be provided.')
        self._contrib = None

    def __setattr__(self, attribute, value):
        """Objectify author."""
        if attribute == 'author':
            value = Redditor(self._reddit, name=value)
        super(LiveUpdate, self).__setattr__(attribute, value)

    def _fetch(self):
        url = API_PATH['live_focus'].format(
            thread_id=self.thread.id, update_id=self.id)
        other = self._reddit.get(url)[0]
        self.__dict__.update(other.__dict__)
        self._fetched = True


class LiveUpdateContribution(object):
    """Provides a set of contribution functions to LiveUpdate."""

    def __init__(self, update):
        """Create an instance of :class:`.LiveUpdateContribution`.

        :param update: An instance of :class:`.LiveUpdate`.

        This instance can be retrieved through ``update.contrib``
        where update is a :class:`.LiveUpdate` instance. E.g.,

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           update = thread['7827987a-c998-11e4-a0b9-22000b6a88d2']
           update.contrib  # LiveUpdateContribution instance
           update.contrib.remove()

        """
        self.update = update

    def remove(self):
        """Remove a live update.

        Usage:

         .. code-block:: python

           thread = reddit.live('ydwwxneu7vsa')
           update = thread['6854605a-efec-11e6-b0c7-0eafac4ff094']
           update.contrib.remove()

        """
        url = API_PATH['live_remove_update'].format(id=self.update.thread.id)
        data = {'id': self.update.fullname}
        self.update.thread._reddit.post(url, data=data)

    def strike(self):
        """Strike a content of a live update.

        .. code-block:: python

           thread = reddit.live('xyu8kmjvfrww')
           update = thread['cb5fe532-dbee-11e6-9a91-0e6d74fabcc4']
           update.contrib.strike()

        To check whether the update is stricken or not, use ``update.stricken``
        attribute. But note that accessing lazy attributes on updates
        (includes ``update.stricken``) may raises ``AttributeError``.
        See :class:`.LiveUpdate` for details.

        """
        url = API_PATH['live_strike'].format(id=self.update.thread.id)
        data = {'id': self.update.fullname}
        self.update.thread._reddit.post(url, data=data)
