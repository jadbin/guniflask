# coding=utf-8

import logging

from flask import Flask


def redirect_logger(name, logger):
    log = logging.getLogger(name)
    log.handlers = logger.handlers
    log.setLevel(logger.level)


def redirect_app_logger(app: Flask, logger):
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
