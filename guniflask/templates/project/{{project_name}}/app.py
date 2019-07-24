# coding=utf-8

import logging

from flask_sqlalchemy import SQLAlchemy

from guniflask.config import Config
from guniflask.security import JwtAuthManager

log = logging.getLogger(__name__)

config = Config()
db = SQLAlchemy()
jwt_manager = JwtAuthManager()


def make_settings(app, settings):
    """
    This function is invoked before initializing app.
    """


def init_app(app, settings):
    """
    This function is invoked before running app.
    """
