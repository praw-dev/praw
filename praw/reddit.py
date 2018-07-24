"""Provide the Reddit class."""
import os

try:
    from update_checker import update_check
    UPDATE_CHECKER_MISSING = False
except ImportError:  # pragma: no cover
    UPDATE_CHECKER_MISSING = True


from prawcore import (Authorizer, DeviceIDAuthorizer, ReadOnlyAuthorizer,
                      Redirect, Requestor, ScriptAuthorizer,
                      TrustedAuthenticator, UntrustedAuthenticator, session)

from .exceptions import ClientException
from .config import Config
from .const import __version__, API_PATH, USER_AGENT_FORMAT, configparser
from .objector import Objector
from . import models


class Reddit(object):
    """The Reddit class provides convenient access to reddit's API.

    Instances of this class are the gateway to interacting with Reddit's API
    through PRAW. The canonical way to obtain an instance of this class is via:


    .. code-block:: python

       import praw
       reddit = praw.Reddit(client_id='CLIENT_ID',
                            client_secret="CLIENT_SECRET", password='PASSWORD',
                            user_agent='USERAGENT', username='USERNAME')

    """

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

        Raise :class:`ClientException` when attempting to unset ``read_only``
        and only the ReadOnlyAuthorizer is available.

        """
        if value:
            self._core = self._read_only_core
        elif self._authorized_core is None:
            raise ClientException('read_only cannot be unset as only the '
                                  'ReadOnlyAuthorizer is available.')
        else:
            self._core = self._authorized_core

    def __enter__(self):
        """Handle the context manager open."""
        return self

    def __exit__(self, *_args):
        """Handle the context manager close."""
        pass

    def __init__(self, site_name=None, requestor_class=None,
                 requestor_kwargs=None, **config_settings):
        """Initialize a Reddit instance.

        :param site_name: The name of a section in your ``praw.ini`` file from
            which to load settings from. This parameter, in tandem with an
            appropriately configured ``praw.ini``, file is useful if you wish
            to easily save credentials for different applications, or
            communicate with other servers running reddit. If ``site_name`` is
            ``None``, then the site name will be looked for in the environment
            variable praw_site. If it is not found there, the DEFAULT site will
            be used.
        :param requestor_class: A class that will be used to create a
            requestor. If not set, use ``prawcore.Requestor`` (default: None).
        :param requestor_kwargs: Dictionary with additional keyword arguments
            used to initialize the requestor (default: None).

        Additional keyword arguments will be used to initialize the
        :class`.Config` object. This can be used to specify configuration
        settings during instantiation of the :class:`.Reddit` instance. For
        more details please see :ref:`configuration`.

        Required settings are:

        * client_id
        * client_secret (for installed applications set this value to ``None``)
        * user_agent

        The ``requestor_class`` and ``requestor_kwargs`` allow for
        customization of the requestor :class`.Reddit` will use. This allows,
        e.g., easily adding behavior to the requestor or wrapping its
        :class`Session` in a caching layer. Example usage:

        .. code-block:: python

           import json, betamax, requests

           class JSONDebugRequestor(Requestor):
               def request(self, *args, **kwargs):
                   response = super().request(*args, **kwargs)
                   print(json.dumps(response.json(), indent=4))
                   return response

           my_session = betamax.Betamax(requests.Session())
           reddit = Reddit(..., requestor_class=JSONDebugRequestor,
                           requestor_kwargs={'session': my_session})

        """
        self._core = self._authorized_core = self._read_only_core = None
        self._objector = None
        self._unique_counter = 0

        try:
            config_section = site_name or os.getenv('praw_site') or 'DEFAULT'
            self.config = Config(config_section, **config_settings)
        except configparser.NoSectionError as exc:
            help_message = ('You provided the name of a praw.ini '
                            'configuration which does not exist.\n\nFor help '
                            'with creating a Reddit instance, visit\n'
                            'https://praw.readthedocs.io/en/latest/code_overvi'
                            'ew/reddit_instance.html\n\n'
                            'For help on configuring PRAW, visit\n'
                            'https://praw.readthedocs.io/en/latest/getting_sta'
                            'rted/configuration.html')
            if site_name is not None:
                exc.message += '\n' + help_message
            raise

        required_message = ('Required configuration setting {!r} missing. \n'
                            'This setting can be provided in a praw.ini file, '
                            'as a keyword argument to the `Reddit` class '
                            'constructor, or as an environment variable.')
        for attribute in ('client_id', 'user_agent'):
            if getattr(self.config, attribute) in (self.config.CONFIG_NOT_SET,
                                                   None):
                raise ClientException(required_message.format(attribute))
        if self.config.client_secret is self.config.CONFIG_NOT_SET:
            raise ClientException(required_message.format('client_secret') +
                                  '\nFor installed applications this value '
                                  'must be set to None via a keyword argument '
                                  'to the `Reddit` class constructor.')

        self._check_for_update()
        self._prepare_objector()
        self._prepare_prawcore(requestor_class, requestor_kwargs)

        self.auth = models.Auth(self, None)
        """An instance of :class:`.Auth`.

        Provides the interface for interacting with installed and web
        applications. See :ref:`auth_url`

        """

        self.front = models.Front(self)
        """An instance of :class:`.Front`.

        Provides the interface for interacting with front page listings. For
        example:

        .. code-block:: python

           for submission in reddit.front.hot():
               print(submission)

        """

        self.inbox = models.Inbox(self, None)
        """An instance of :class:`.Inbox`.

        Provides the interface to a user's inbox which produces
        :class:`.Message`, :class:`.Comment`, and :class:`.Submission`
        instances. For example to iterate through comments which mention the
        authorized user run:

        .. code-block:: python

           for comment in reddit.inbox.mentions():
               print(comment)

        """

        self.live = models.LiveHelper(self, None)
        """An instance of :class:`.LiveHelper`.

        Provides the interface for working with :class:`.LiveThread`
        instances. At present only new LiveThreads can be created.

        .. code-block:: python

           reddit.live.create('title', 'description')

        """

        self.multireddit = models.MultiredditHelper(self, None)
        """An instance of :class:`.MultiredditHelper`.

        Provides the interface to working with :class:`.Multireddit`
        instances. For example you can obtain a :class:`.Multireddit` instance
        via:

        .. code-block:: python

           reddit.multireddit('samuraisam', 'programming')

        """

        self.subreddit = models.SubredditHelper(self, None)
        """An instance of :class:`.SubredditHelper`.

        Provides the interface to working with :class:`.Subreddit`
        instances. For example to create a Subreddit run:

        .. code-block:: python

           reddit.subreddit.create('coolnewsubname')

        To obtain a lazy a :class:`.Subreddit` instance run:

        .. code-block:: python

           reddit.subreddit('redditdev')

        Note that multiple subreddits can be combined and filtered views of
        /r/all can also be used just like a subreddit:

        .. code-block:: python

           reddit.subreddit('redditdev+learnpython+botwatch')
           reddit.subreddit('all-redditdev-learnpython')

        """

        self.subreddits = models.Subreddits(self, None)
        """An instance of :class:`.Subreddits`.

        Provides the interface for :class:`.Subreddit` discovery. For example
        to iterate over the set of default subreddits run:

        .. code-block:: python

           for subreddit in reddit.subreddits.default(limit=None):
               print(subreddit)

        """

        self.user = models.User(self)
        """An instance of :class:`.User`.

        Provides the interface to the currently authorized
        :class:`.Redditor`. For example to get the name of the current user
        run:

        .. code-block:: python

           print(reddit.user.me())

        """

    def _check_for_update(self):
        if UPDATE_CHECKER_MISSING:
            return
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
                    'Button': models.Button,
                    'Image': models.Image,
                    'LabeledMulti': models.Multireddit,
                    'Listing': models.Listing,
                    'LiveUpdate': models.LiveUpdate,
                    'LiveUpdateEvent': models.LiveThread,
                    'MenuLink': models.MenuLink,
                    'ModmailAction': models.ModmailAction,
                    'ModmailConversation': models.ModmailConversation,
                    'ModmailMessage': models.ModmailMessage,
                    'Submenu': models.Submenu,
                    'UserList': models.RedditorList,
                    'button': models.ButtonWidget,
                    'calendar': models.Calendar,
                    'community-list': models.CommunityList,
                    'custom': models.CustomWidget,
                    'id-card': models.IDCard,
                    'image': models.ImageWidget,
                    'modaction': models.ModAction,
                    'moderators': models.ModeratorsWidget,
                    'menu': models.Menu,
                    'more': models.MoreComments,
                    'stylesheet': models.Stylesheet,
                    'subreddit-rules': models.RulesWidget,
                    'textarea': models.TextArea}
        for kind, klass in mappings.items():
            self._objector.register(kind, klass)

    def _prepare_prawcore(self, requestor_class=None, requestor_kwargs=None):
        requestor_class = requestor_class or Requestor
        requestor_kwargs = requestor_kwargs or {}

        requestor = requestor_class(
            USER_AGENT_FORMAT.format(self.config.user_agent),
            self.config.oauth_url, self.config.reddit_url,
            **requestor_kwargs)

        if self.config.client_secret:
            self._prepare_trusted_prawcore(requestor)
        else:
            self._prepare_untrusted_prawcore(requestor)

    def _prepare_trusted_prawcore(self, requestor):
        authenticator = TrustedAuthenticator(requestor, self.config.client_id,
                                             self.config.client_secret,
                                             self.config.redirect_uri)
        read_only_authorizer = ReadOnlyAuthorizer(authenticator)
        self._read_only_core = session(read_only_authorizer)

        if self.config.username and self.config.password:
            script_authorizer = ScriptAuthorizer(
                authenticator, self.config.username, self.config.password)
            self._core = self._authorized_core = session(script_authorizer)
        elif self.config.refresh_token:
            authorizer = Authorizer(authenticator, self.config.refresh_token)
            self._core = self._authorized_core = session(authorizer)
        else:
            self._core = self._read_only_core

    def _prepare_untrusted_prawcore(self, requestor):
        authenticator = UntrustedAuthenticator(requestor,
                                               self.config.client_id,
                                               self.config.redirect_uri)
        read_only_authorizer = DeviceIDAuthorizer(authenticator)
        self._read_only_core = session(read_only_authorizer)
        if self.config.refresh_token:
            authorizer = Authorizer(authenticator, self.config.refresh_token)
            self._core = self._authorized_core = session(authorizer)
        else:
            self._core = self._read_only_core

    def comment(self,  # pylint: disable=invalid-name
                id=None,  # pylint: disable=redefined-builtin
                url=None):
        """Return a lazy instance of :class:`~.Comment` for ``id``.

        :param id: The ID of the comment.

        :param url: A permalink pointing to the comment.

        .. note:: If you want to obtain the comment's replies, you will need to
                  call :meth:`~.Comment.refresh` on the returned
                  :class:`.Comment`.

        """
        return models.Comment(self, id=id, url=url)

    def domain(self, domain):
        """Return an instance of :class:`.DomainListing`.

        :param domain: The domain to obtain submission listings for.

        """
        return models.DomainListing(self, domain)

    def get(self, path, params=None):
        """Return parsed objects returned from a GET request to ``path``.

        :param path: The path to fetch.
        :param params: The query parameters to add to the request (default:
            None).

        """
        data = self.request('GET', path, params=params)
        return self._objector.objectify(data)

    def info(self, fullnames=None, url=None):
        """Fetch information about each item in ``fullnames`` or from ``url``.

        :param fullnames: A list of fullnames for comments, submissions, and/or
            subreddits.
        :param url: A url (as a string) to retrieve lists of link submissions
            from.
        :returns: A generator that yields found items in their relative order.

        Items that cannot be matched will not be generated. Requests will be
        issued in batches for each 100 fullnames.

        .. note:: For comments that are retrieved via this method, if you want
                  to obtain its replies, you will need to call
                  :meth:`~.Comment.refresh` on the yielded :class:`.Comment`.

        .. note:: When using the URL option, it is important to be aware that
                  URLs are treated literally by Reddit's API. As such, the URLs
                  "youtube.com" and "https://www.youtube.com" will provide a
                  different set of submissions.

        """
        if bool(fullnames) == bool(url):
            raise TypeError('Either `fullnames` or `url` must be provided.')

        elif fullnames:
            if not isinstance(fullnames, list):
                raise TypeError('fullnames must be a list')

            def generator():
                for position in range(0, len(fullnames), 100):
                    fullname_chunk = fullnames[position:position + 100]
                    params = {'id': ','.join(fullname_chunk)}
                    for result in self.get(API_PATH['info'], params=params):
                        yield result

            return generator()

        else:
            try:
                params = {'url': url}
                url_list = [result for result in
                            self.get(API_PATH['info'], params=params)]
                return url_list
            except Exception:
                raise TypeError('Invalid URL or no posts exist')

    def patch(self, path, data=None):
        """Return parsed objects returned from a PATCH request to ``path``.

        :param path: The path to fetch.
        :param data: Dictionary, bytes, or file-like object to send in the body
            of the request (default: None).

        """
        data = self.request('PATCH', path, data=data)
        return self._objector.objectify(data)

    def post(self, path, data=None, files=None, params=None):
        """Return parsed objects returned from a POST request to ``path``.

        :param path: The path to fetch.
        :param data: Dictionary, bytes, or file-like object to send in the body
            of the request (default: None).
        :param files: Dictionary, filename to file (like) object mapping
            (default: None).
        :param params: The query parameters to add to the request (default:
            None).

        """
        data = self.request('POST', path, data=data or {}, files=files,
                            params=params)
        return self._objector.objectify(data)

    def random_subreddit(self, nsfw=False):
        """Return a random lazy instance of :class:`~.Subreddit`.

        :param nsfw: Return a random NSFW (not safe for work) subreddit
            (default: False).

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

    def request(self, method, path, params=None, data=None, files=None):
        """Return the parsed JSON data returned from a request to URL.

        :param method: The HTTP method (e.g., GET, POST, PUT, DELETE).
        :param path: The path to fetch.
        :param params: The query parameters to add to the request (default:
            None).
        :param data: Dictionary, bytes, or file-like object to send in the body
            of the request (default: None).
        :param files: Dictionary, filename to file (like) object mapping
            (default: None).

        """
        return self._core.request(method, path, data=data, files=files,
                                  params=params)

    def submission(  # pylint: disable=invalid-name,redefined-builtin
            self, id=None, url=None):
        """Return a lazy instance of :class:`~.Submission`.

        :param id: A reddit base36 submission ID, e.g., ``2gmzqe``.
        :param url: A URL supported by
            :meth:`~praw.models.Submission.id_from_url`.`.

        Either ``id`` or ``url`` can be provided, but not both.

        """
        return models.Submission(self, id=id, url=url)
