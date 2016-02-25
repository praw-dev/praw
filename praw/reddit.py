"""Provide the Reddit class."""
import os

from prawcore import Authenticator, Authorizer, Requestor
from update_checker import update_check

from .config import Config
from .const import __version__


class Reddit(object):
    """Provide convenient access to reddit's API."""

    update_checked = False

    def __init__(self, site_name=None, **config_settings):
        """Initialize a Reddit instance.

        :param site_name: The name of a section in your ``praw.ini`` file from
            which to load settings from. This parameter in tandem with an
            appropriately configured ``praw.ini`` file is useful if you wish to
            easily save credentials for different applications, or communicate
            with other servers running reddit. If ``site_name`` is ``None``,
            then the site name will be looked for in the environment variable
            PRAW_SITE. If it is not found there, the default site name
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
        self.config = Config(site_name or os.getenv('PRAW_SITE') or 'reddit',
                             **settings)
        self._check_for_update()
        authenticator = Authenticator(Requestor(self.config.user_agent),
                                      self.config.client_id,
                                      self.config.client_secret)

    def _check_for_update(self):
        if not self.update_checked and self.config.check_for_updates:
            update_check(__package__, __version__)
            self.update_checked = True
