import logging

from flask import Flask
from guniflask.config import Settings

log = logging.getLogger(__name__)


def make_settings(app: Flask, settings: Settings):
    pass


def init_app(app: Flask, settings: Settings):
    pass
