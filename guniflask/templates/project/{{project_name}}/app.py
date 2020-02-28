# coding=utf-8

import logging

from flask_sqlalchemy import SQLAlchemy

log = logging.getLogger(__name__)

db = SQLAlchemy()


def make_settings(app, settings):
    """
    This function is invoked before initializing app.
    """


def init_app(app, settings):
    """
    This function is invoked before running app.
    """
    db.init_app(app)
