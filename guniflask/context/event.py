# coding=utf-8

__all__ = ['ApplicationEvent',
           'ContextRefreshedEvent',
           'ContextClosedEvent']


class ApplicationEvent:
    def __init__(self, source):
        self.source = source


class ContextRefreshedEvent(ApplicationEvent):
    pass


class ContextClosedEvent(ApplicationEvent):
    pass
