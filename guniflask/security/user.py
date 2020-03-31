# coding=utf-8

from guniflask.security.user_details import UserDetails

__all__ = ['User']


class User(UserDetails):
    default_role_prefix = 'role_'

    def __init__(self, username=None, password=None, authorities=None):
        self._username = username
        self._password = password
        self._authorities = set()
        if authorities:
            self._authorities.update(authorities)

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def authorities(self):
        return self._authorities

    def has_authority(self, authority):
        return self.has_any_authority(authority)

    def has_any_authority(self, *authorities):
        return self._has_any_authority_name(None, *authorities)

    def has_role(self, role):
        return self.has_any_role(role)

    def has_any_role(self, *roles):
        return self._has_any_authority_name(self.default_role_prefix, *roles)

    def _has_any_authority_name(self, prefix, *roles):
        for role in roles:
            r = self._role_with_prefix(prefix, role)
            if r in self.authorities:
                return True
        return False

    @staticmethod
    def _role_with_prefix(prefix, role):
        if role is None or prefix is None:
            return role
        if role.startswith(prefix):
            return role
        return prefix + role
