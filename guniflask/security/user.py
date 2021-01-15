from guniflask.security.user_details import UserDetails


class User(UserDetails):
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
