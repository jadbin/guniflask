from guniflask.security import has_role
from guniflask.web import blueprint, post_route, get_route

from ..services.account_service import AccountService


@blueprint
class AccountController:
    def __init__(self, accounts: AccountService):
        self.accounts = accounts

    @post_route('/login')
    def login(self, username: str, password: str):
        return self.accounts.login(username, password)

    @has_role('admin')
    @get_route('/accounts/account-info')
    def get_account_info(self):
        return self.accounts.get_account_info()

    @has_role('admin')
    @get_route('/accounts/account-info-gevent')
    def get_account_info_by_gevent(self):
        return self.accounts.get_account_info_by_gevent()
