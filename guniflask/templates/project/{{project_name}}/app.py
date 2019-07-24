# coding=utf-8

import logging

from flask_sqlalchemy import SQLAlchemy

from guniflask.config import Config
from guniflask.security import JwtAuthManager

log = logging.getLogger(__name__)

config = Config()
db = SQLAlchemy()
jwt_manager = JwtAuthManager()

app_default_settings = {
    'debug': False,
    'cors': True,
    # Flask-SQLAlchemy
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
}


def make_settings(app, settings):
    """
    This function is invoked before initializing app.
    """


def init_app(app, settings):
    """
    This function is invoked before running app.
    """
