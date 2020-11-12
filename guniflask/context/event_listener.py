from abc import ABCMeta, abstractmethod

from guniflask.context.event import ApplicationEvent


class ApplicationEventListener(metaclass=ABCMeta):

    @abstractmethod
    def on_application_event(self, application_event: ApplicationEvent):
        pass  # pragma: no cover
