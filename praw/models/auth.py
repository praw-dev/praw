"""Provide the Auth class."""
from prawcore import (Authorizer, ImplicitAuthorizer, TrustedAuthenticator,
                      UntrustedAuthenticator, session)

from .base import PRAWBase
from ..exceptions import ClientException


class Auth(PRAWBase):
    """Auth provides an interface to Reddit's authorization."""

    def authorize(self, code):
        """Complete the web authorization flow and return the refresh token.

        :param code: The code obtained through the request to the redirect uri.
        :returns: The obtained refresh token, if available, otherwise ``None``.

        The session's active authorization will be updated upon success.

        """
        authenticator = self._reddit._read_only_core._authorizer._authenticator
        if not isinstance(authenticator, TrustedAuthenticator) or \
           self._reddit.config.username:
            raise ClientException('authorize can only be used with web apps.')
        authorizer = Authorizer(authenticator)
        authorizer.authorize(code)
        authorized_session = session(authorizer)
        self._reddit._core = self._reddit._authorized_core = authorized_session
        return authorizer.refresh_token

    def implicit(self, access_token, expires_in, scope):
        """Set the active authorization to be an implicit authorization.

        :param access_token: The access_token obtained from Reddit's callback.
        :param expires_in: The number of seconds the ``access_token`` is valid
            for. The origin of this value was returned from Reddit's callback.
            You may need to subtract an offset before passing in this number to
            account for a delay between when Reddit prepared the response, and
            when you make this function call.
        :param scope: A space-delimited string of Reddit OAuth2 scope names as
            returned from Reddit's callback.

        Raise class:`.ClientException` if :class:`.Reddit` was initialized for
        a non-installed application type.

        """
        authenticator = self._reddit._read_only_core._authorizer._authenticator
        if not isinstance(authenticator, UntrustedAuthenticator):
            raise ClientException('implicit can only be used with installed '
                                  'apps.')
        implicit_session = session(ImplicitAuthorizer(
            authenticator, access_token, expires_in, scope))
        self._reddit._core = self._reddit._authorized_core = implicit_session

    def scopes(self):
        """Return a set of scopes included in the current authorization.

        For read-only authorizations this should return ``{'*'}``.

        """
        authorizer = self._reddit._core._authorizer
        if not authorizer.is_valid():
            authorizer.refresh()
        return authorizer.scopes

    def url(self, scopes, state, duration='permanent', implicit=False):
        """Return the URL used out-of-band to grant access to your application.

        :param scopes: A list of OAuth scopes to request authorization for.
        :param state: A string that will be reflected in the callback to
            ``redirect_uri``. This value should be temporarily unique to the
            client for whom the URL was generated for.
        :param duration: Either ``permanent`` or ``temporary`` (default:
            permanent). ``temporary`` authorizations generate access tokens
            that last only 1 hour. ``permanent`` authorizations additionally
            generate a refresh token that can be indefinitely used to generate
            new hour-long access tokens. This value is ignored when
            ``implicit=True``.
        :param implicit: For **installed** applications, this value can be set
            to use the implicit, rather than the code flow. When True, the
            ``duration`` argument has no effect as only temporary tokens can be
            retrieved.

        """
        authenticator = self._reddit._read_only_core._authorizer._authenticator
        if authenticator.redirect_uri is self._reddit.config.CONFIG_NOT_SET:
            raise ClientException('redirect_uri must be provided')
        if isinstance(authenticator, UntrustedAuthenticator):
            return authenticator.authorize_url(
                'temporary' if implicit else duration, scopes, state,
                implicit=implicit)
        elif implicit:
            raise ClientException('implicit can only be set for installed '
                                  'applications')
        return authenticator.authorize_url(duration, scopes, state)
