from typing import List

from guniflask.beans.lifecycle import InitializingBean
from guniflask.security.authentication import Authentication
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.security.authentication_provider import AuthenticationProvider
from guniflask.security.errors import AuthenticationError, ProviderNotFoundError


class ProviderManager(AuthenticationManager, InitializingBean):
    def __init__(self, parent: AuthenticationManager = None, providers: List[AuthenticationProvider] = None):
        self._parent = parent
        self._providers: List[AuthenticationProvider] = []
        if providers:
            for p in providers:
                self._providers.append(p)

    def authenticate(self, authentication: Authentication):
        to_test = type(authentication)
        last_error = None
        result = None

        for provider in self._providers:
            if not provider.supports(to_test):
                continue
            try:
                result = provider.authenticate(authentication)
            except AuthenticationError as e:
                last_error = e
            else:
                if result is not None:
                    if result.details is None:
                        result.details = authentication.details
                    break

        if result is None and self._parent is not None:
            try:
                result = self._parent.authenticate(authentication)
            except ProviderNotFoundError:
                pass
            except AuthenticationError as e:
                last_error = e

        if result is None:
            if last_error is None:
                last_error = ProviderNotFoundError(f'No authentication provider for {to_test.__name__}')
            raise last_error

        return result

    def after_properties_set(self):
        self._check_state()

    def _check_state(self):
        if not self._parent and not self._providers:
            raise ValueError('A parent authentication manager or a list of authentication provides is required')
