# coding=utf-8

import logging
from abc import ABCMeta, abstractmethod

from guniflask.beans.factory_post_processor import BeanFactoryPostProcessor
from guniflask.context.event_listener import ApplicationEventListener
from guniflask.beans.factory import BeanFactory

__all__ = ['BeanContext', 'BeanContextAware']

log = logging.getLogger(__name__)


class BeanContext(BeanFactory, metaclass=ABCMeta):

    @abstractmethod
    def add_application_listener(self, listener: ApplicationEventListener):
        pass

    @abstractmethod
    def add_bean_factory_post_processor(self, post_processor: BeanFactoryPostProcessor):
        pass

    @abstractmethod
    def refresh(self):
        pass

    @abstractmethod
    def close(self):
        pass


class BeanContextAware(metaclass=ABCMeta):
    @abstractmethod
    def set_bean_context(self, bean_context: BeanContext):
        pass
