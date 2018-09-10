# coding=utf-8

active_profiles = None

cors = True

SQLALCHEMY_TRACK_MODIFICATIONS = False


def make_settings(app, settings):
    """
    This function is invoked before initializing app.
    """
