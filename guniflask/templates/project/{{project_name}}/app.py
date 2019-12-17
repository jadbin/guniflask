# coding=utf-8

import logging

from guniflask.app import new_sqlalchemy

log = logging.getLogger(__name__)

db = new_sqlalchemy()


def make_settings(app, settings):
    """
    This function is invoked before initializing app.
    """


def init_app(app, settings):
    """
    This function is invoked before running app.
    """
    db.init_app(app)
