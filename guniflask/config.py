# coding=utf-8

from flask import has_app_context, current_app


class ConfigProxy:
    @property
    def settings(self):
        if has_app_context():
            return current_app.config['GUNIFLASK_SETTINGS']
        raise RuntimeError("Cannot access 'settings' without app context")
