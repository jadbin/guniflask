from flask import abort
from guniflask.context import service

from ..config.jwt_config import jwt_manager


@service
class AccountService:
    accounts = {
        'root': {
            'authorities': ['role_admin'],
            'password': '123456',
        }
    }

    def login(self, username: str, password: str):
        if username not in self.accounts or self.accounts[username]['password'] != password:
            return abort(403)
        account = self.accounts[username]
        token = jwt_manager.create_access_token(authorities=account['authorities'], username=username)
        return {
            'username': username,
            'access_token': token,
        }

    def get(self, username: str):
        if username not in self.accounts:
            return abort(404)
        return {
            'username': username,
            'authorities': self.accounts[username]['authorities']
        }
