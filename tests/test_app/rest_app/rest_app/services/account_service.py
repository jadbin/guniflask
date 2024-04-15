import gevent
from flask import abort

from guniflask.context import service
from guniflask.security import current_user
from guniflask.utils.context import run_with_context
from ..config.jwt_config import jwt_manager


@service
class AccountService:
    accounts = {
        'root': {
            'authorities': ['role_admin'],
            'password': '123456',
        }
    }

    def login(self, username: str, password: str) -> dict:
        if username not in self.accounts or self.accounts[username]['password'] != password:
            return abort(403)
        account = self.accounts[username]
        token = jwt_manager.create_access_token(authorities=account['authorities'], username=username)
        return {
            'username': username,
            'access_token': token,
        }

    def get_account_info(self) -> dict:
        return self._do_get_account_info()

    def get_account_info_by_gevent(self) -> dict:
        job = gevent.spawn(
            run_with_context(
                self._do_get_account_info
            )
        )
        gevent.wait([job])
        return job.get()

    def _do_get_account_info(self) -> dict:
        return {
            'username': current_user.username,
            'authorities': list(current_user.authorities),
        }
