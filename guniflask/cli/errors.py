# coding=utf-8

__all__ = ['UsageError', 'AbortedError', 'TemplateError']


class UsageError(Exception):
    """
    Usage error
    """

    def __init__(self, *args, print_help=False, **kwargs):
        self.print_help = print_help
        super().__init__(*args, **kwargs)


class AbortedError(Exception):
    """
    Aborted error
    """


class TemplateError(Exception):
    """
    Template error
    """
