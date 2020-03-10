# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.context.event import ApplicationEvent

__all__ = ['ApplicationEventListener']


class ApplicationEventListener(metaclass=ABCMeta):

    @abstractmethod
    def on_application_event(self, application_event: ApplicationEvent):
        pass
