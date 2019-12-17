# coding=utf-8


__all__ = ['User', 'AnonymousUser']


class User:
    ROLE_PREFIX = 'role_'

    def __init__(self, authorities=None, **kwargs):
        self.authorities = []
        if authorities is not None:
            for a in authorities:
                self.authorities.append(a.lower())
        self._authorities_set = set(self.authorities)
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def is_authenticated(self):
        return True

    def has_authority(self, authority):
        authority = authority.lower()
        return authority in self._authorities_set

    def has_any_authority(self, *authorities):
        for a in authorities:
            if self.has_authority(a):
                return True
        return False

    def has_role(self, role):
        return self.has_authority(self._get_role_with_prefix(self.ROLE_PREFIX, role))

    def has_any_role(self, *roles):
        for r in roles:
            if self.has_role(r):
                return True
        return False

    @staticmethod
    def _get_role_with_prefix(prefix, role):
        if role is None or prefix is None:
            return role
        if role.startswith(prefix):
            return role
        return prefix + role


class AnonymousUser(User):
    def __init__(self, authorities=None, **kwargs):
        super().__init__(**kwargs)

    @property
    def is_authenticated(self):
        return False
