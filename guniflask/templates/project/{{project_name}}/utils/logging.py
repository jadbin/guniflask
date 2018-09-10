# coding=utf-8

import logging


def redirect_logger(name, logger):
    log = logging.getLogger(name)
    log.handlers = logger.handlers
    log.setLevel(logger.level)


def redirect_app_logger(app, logger):
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
