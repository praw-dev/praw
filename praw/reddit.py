"""Provide the Reddit class."""
import os

from six import iteritems
from update_checker import update_check
from prawcore import (Authenticator, ReadOnlyAuthorizer, Redirect, Requestor,
                      ScriptAuthorizer, session)

from .exceptions import ClientException
from .config import Config
from .const import __version__, API_PATH, USER_AGENT_FORMAT
from .objector import Objector
from . import models


class Reddit(object):
    """Provide convenient access to reddit's API."""

    update_checked = False

    @property
    def _next_unique(self):
        value = self._unique_counter
        self._unique_counter += 1
        return value

    @property
    def read_only(self):
        """Return True when using the ReadOnlyAuthorizer."""
        return self._core == self._read_only_core

    @read_only.setter
    def read_only(self, value):
        """Set or unset the use of the ReadOnlyAuthorizer.

        Raise ``ClientException`` when attempting to unset ``read_only`` and
        only the ReadOnlyAuthorizer is available.

        """
        if value:
            self._core = self._read_only_core
        elif self._authorized_core is None:
            raise ClientException('read_only cannot be set as only the '
                                  'ReadOnlyAuthorizer is available.')
        else:
            self._core = self._authorized_core

    def __enter__(self):
        """Handle the context manager open."""
        return self

    def __exit__(self, *_args):
        """Handle the context manager close."""
        pass

    def __init__(self, site_name=None, **config_settings):
        """Initialize a Reddit instance.

        :param site_name: The name of a section in your ``praw.ini`` file from
            which to load settings from. This parameter in tandem with an
            appropriately configured ``praw.ini`` file is useful if you wish to
            easily save credentials for different applications, or communicate
            with other servers running reddit. If ``site_name`` is ``None``,
            then the site name will be looked for in the environment variable
            praw_site. If it is not found there, the default site name
            ``reddit`` will be used.

        Additional keyword arguments will be used to initialize the ``Config``
        object. This can be used to specify configuration settings during
        instantiation of the ``Reddit`` instance. For more details please see:
        https://praw.readthedocs.org/en/stable/pages/configuration_files.html

        Required settings are:

        * client_id
        * client_secret
        * user_agent

        """
        self._core = self._authorized_core = self._read_only_core = None
        self._objector = None
        self._unique_counter = 0
        self.config = Config(site_name or os.getenv('praw_site') or 'reddit',
                             **config_settings)

        for attribute in ['client_id', 'client_secret', 'user_agent']:
            if not getattr(self.config, attribute):
                message = ('Required configuration setting {!r} missing. \n'
                           'This setting can be provided in a praw.ini file, '
                           'as a keyword argument to the `Reddit` class '
                           'constructor, or as an environment variable.')
                raise ClientException(message.format(attribute))

        self._check_for_update()
        self._prepare_objector()
        self._prepare_prawcore()
        self.front = models.Front(self)
        self.inbox = models.Inbox(self, None)
        self.user = models.User(self, None)

    def _check_for_update(self):
        if not Reddit.update_checked and self.config.check_for_updates:
            update_check(__package__, __version__)
            Reddit.update_checked = True

    def _prepare_objector(self):
        self._objector = Objector(self)
        mappings = {self.config.kinds['comment']: models.Comment,
                    self.config.kinds['message']: models.Message,
                    self.config.kinds['redditor']: models.Redditor,
                    self.config.kinds['submission']: models.Submission,
                    self.config.kinds['subreddit']: models.Subreddit,
                    'LabeledMulti': models.Multireddit,
                    'Listing': models.Listing,
                    'UserList': models.RedditorList,
                    'modaction': models.ModAction,
                    'more': models.MoreComments,
                    'wikipage': models.WikiPage,
                    'wikipagelisting': models.WikiPageList}
        for kind, klass in iteritems(mappings):
            self._objector.register(kind, klass)

    def _prepare_prawcore(self):
        requestor = Requestor(USER_AGENT_FORMAT.format(self.config.user_agent),
                              self.config.oauth_url, self.config.reddit_url)
        authenticator = Authenticator(requestor, self.config.client_id,
                                      self.config.client_secret)
        read_only_authorizer = ReadOnlyAuthorizer(authenticator)
        self._read_only_core = session(read_only_authorizer)

        if self.config.username and self.config.password:
            script_authorizer = ScriptAuthorizer(
                authenticator, self.config.username, self.config.password)
            self._core = self._authorized_core = session(script_authorizer)
        else:
            self._core = self._read_only_core

    def comment(self, id):
        """Return a lazy instance of :class:`~.Comment` for ``id``.

        :param id: The ID of the comment.

        """
        return models.Comment(self, id=id)

    def get(self, path, params=None):
        """Return parsed objects returned from a GET request to ``path``.

        :param path: The path to fetch.
        :param params: The query parameters to add to the request (Default:
            None).

        """
        data = self.request('GET', path, params=params)
        return self._objector.objectify(data)

    def post(self, path, data=None, params=None):
        """Return parsed objects returned from a POST request to ``path``.

        :param path: The path to fetch.
        :param data: Dictionary, bytes, or file-like object to send in the body
        of the request.
        :param params: The query parameters to add to the request (Default:
            None).

        """
        data = self.request('POST', path, data=data, params=params)
        return self._objector.objectify(data)

    def random_subreddit(self, nsfw=False):
        """Return a random lazy instance of :class:`~.Subreddit`.

        :param nsfw: Return a random NSFW (not safe for work) subreddit
            (Default: False).

        """
        url = API_PATH['subreddit'].format(subreddit='randnsfw' if nsfw
                                           else 'random')
        path = None
        try:
            self.get(url, params={'unique': self._next_unique})
        except Redirect as redirect:
            path = redirect.path
        return models.Subreddit(self, path.split('/')[2])

    def redditor(self, name):
        """Return a lazy instance of :class:`~.Redditor` for ``name``.

        :param name: The name of the redditor.

        """
        return models.Redditor(self, name)

    def request(self, method, path, params=None, data=None):
        """Return the parsed JSON data returned from a request to URL.

        :param method: The HTTP method (e.g., GET, POST, PUT, DELETE).
        :param path: The path to fetch.
        :param params: The query parameters to add to the request (Default:
            None).
        :param data: Dictionary, bytes, or file-like object to send in the body
        of the request.

        """
        if not self._core._authorizer.is_valid():
            self._core._authorizer.refresh()
        return self._core.request(method, path, params=params, data=data)

    def submission(  # pylint: disable=invalid-name,redefined-builtin
            self, id=None, url=None):
        """Return a lazy instance of :class:`~.Submission`.

        :param id: A reddit base64 submission ID, e.g., ``2gmzqe``.
        :param url: A URL supported by :meth:`Submission.id_from_url`.

        Either ``id`` or ``url`` can be provided, but not both.

        """
        return models.Submission(self, id=id, url=url)

    def subreddit(self, name):
        """Return a lazy instance of :class:`~.Subreddit` for ``name``.

        :param name: The name of the subreddit.

        """
        lower_name = name.lower()
        if lower_name == 'random':
            return self.random_subreddit()
        elif lower_name == 'randnsfw':
            return self.random_subreddit(nsfw=True)
        return models.Subreddit(self, name)
