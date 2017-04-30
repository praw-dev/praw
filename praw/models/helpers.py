"""Provide the helper classes."""
from json import dumps

from ..const import API_PATH
from .base import PRAWBase
from .reddit.live import LiveThread
from .reddit.multi import Multireddit, Subreddit


class LiveHelper(PRAWBase):
    """Provide a set of functions to interact with LiveThreads."""

    def __call__(self, id):  # pylint: disable=invalid-name,redefined-builtin
        """Return a new lazy instance of :class:`~.LiveThread`.

        This method is intended to be used as:

        .. code:: python

            livethread = reddit.live('ukaeu1ik4sw5')

        :param id: A live thread ID, e.g., ``ukaeu1ik4sw5``.
        """
        return LiveThread(self._reddit, id=id)

    def info(self, ids):
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

        .. code:: python

            ids = ['3rgnbke2rai6hen7ciytwcxadi',
                   'sw7bubeycai6hey4ciytwamw3a',
                   't8jnufucss07']
            for thread in reddit.live.info(ids)
                print(thread.title)

        """
        if not isinstance(ids, list):
            raise TypeError('ids must be a list')

        def generator():
            for position in range(0, len(ids), 100):
                ids_chunk = ids[position:position + 100]
                url = API_PATH['live_info'].format(ids=','.join(ids_chunk))
                params = {'limit': 100}  # 25 is used if not specified
                for result in self._reddit.get(url, params=params):
                    yield result

        return generator()

    def create(self, title, description=None, nsfw=False, resources=None):
        """Create a new LiveThread.

        :param title: The title of the new LiveThread.
        :param description: (Optional) The new LiveThread's description.
        :param nsfw: (boolean) Indicate whether this thread is not safe for
            work (default: False).
        :param resources: (Optional) Markdown formatted information that is
            useful for the LiveThread.
        :returns: The new LiveThread object.

        """
        return self._reddit.post(API_PATH['livecreate'], data={
            'description': description, 'nsfw': nsfw, 'resources': resources,
            'title': title})

    def now(self):
        """Get the currently featured live thread.

        :returns: The :class:`.LiveThread` object, or ``None`` if there is
            no currently featured live thread.

        Usage:

        .. code-block:: python

        thread = reddit.live.now()  # LiveThread object or None

        """
        return self._reddit.get(API_PATH['live_now'])


class MultiredditHelper(PRAWBase):
    """Provide a set of functions to interact with Multireddits."""

    def __call__(self, redditor, name):
        """Return a lazy instance of :class:`~.Multireddit`.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance who owns the multireddit.
        :param name: The name of the multireddit.

        """
        path = '/user/{}/m/{}'.format(redditor, name)
        return Multireddit(self._reddit, _data={'name': name, 'path': path})

    def create(self, display_name, subreddits, description_md=None,
               icon_name=None, key_color=None, visibility='private',
               weighting_scheme='classic'):
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
        model = {'description_md': description_md,
                 'display_name': display_name,
                 'icon_name': icon_name,
                 'key_color': key_color,
                 'subreddits': [{'name': str(sub)} for sub in subreddits],
                 'visibility': visibility,
                 'weighting_scheme': weighting_scheme}
        return self._reddit.post(API_PATH['multireddit_base'],
                                 data={'model': dumps(model)})


class SubredditHelper(PRAWBase):
    """Provide a set of functions to interact with Subreddits."""

    def __call__(self, display_name):
        """Return a lazy instance of :class:`~.Subreddit`.

        :param display_name: The name of the subreddit.
        """
        lower_name = display_name.lower()

        if lower_name == 'random':
            return self._reddit.random_subreddit()
        elif lower_name == 'randnsfw':
            return self._reddit.random_subreddit(nsfw=True)

        return Subreddit(self._reddit, display_name=display_name)

    def create(self, name, title=None, link_type='any',
               subreddit_type='public', wikimode='disabled', **other_settings):
        """Create a new subreddit.

        :param name: The name for the new subreddit.

        :param title: The title of the subreddit. When ``None`` or ``''`` use
            the value of ``name``.

        :param link_type: The types of submissions users can make.
            One of ``any``, ``link``, ``self`` (default: any).
        :param subreddit_type: One of ``archived``, ``employees_only``,
            ``gold_only``, ``gold_restricted``, ``private``, ``public``,
            ``restricted`` (default: public).
        :param wikimode: One of  ``anyone``, ``disabled``, ``modonly``.

        See :meth:`~.SubredditModeration.update` for documentation of other
        available settings.

        Any keyword parameters not provided, or set explicitly to None, will
        take on a default value assigned by the Reddit server.

        """
        Subreddit._create_or_update(_reddit=self._reddit, name=name,
                                    link_type=link_type,
                                    subreddit_type=subreddit_type,
                                    title=title or name, wikimode=wikimode,
                                    **other_settings)
        return self(name)
