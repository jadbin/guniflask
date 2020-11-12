import logging
from abc import ABCMeta, abstractmethod

from guniflask.beans.factory import BeanFactory
from guniflask.beans.factory_post_processor import BeanFactoryPostProcessor
from guniflask.context.event_listener import ApplicationEventListener

log = logging.getLogger(__name__)


class BeanContext(BeanFactory, metaclass=ABCMeta):

    @abstractmethod
    def add_application_listener(self, listener: ApplicationEventListener):
        pass  # pragma: no cover

    @abstractmethod
    def add_bean_factory_post_processor(self, post_processor: BeanFactoryPostProcessor):
        pass  # pragma: no cover

    @abstractmethod
    def refresh(self):
        pass  # pragma: no cover

    @abstractmethod
    def close(self):
        pass  # pragma: no cover


class BeanContextAware(metaclass=ABCMeta):
    @abstractmethod
    def set_bean_context(self, bean_context: BeanContext):
        pass  # pragma: no cover
