# coding=utf-8

import inspect
from typing import Type

from guniflask.beans.factory import BeanFactory
from guniflask.context.event import ApplicationEvent
from guniflask.context.event_listener import ApplicationEventListener

__all__ = ['ApplicationEventPublisher']


class ApplicationEventPublisher:
    def __init__(self, bean_factory: BeanFactory):
        self._bean_factory = bean_factory
        self._app_listeners = set()
        self._app_listener_beans = set()

    def add_application_listener(self, listener: ApplicationEventListener):
        self._app_listeners.add(listener)

    def add_application_listener_bean(self, bean_name: str):
        self._app_listener_beans.add(bean_name)

    def publish_event(self, event: ApplicationEvent):
        for listener in self._get_application_listeners():
            assert isinstance(listener, ApplicationEventListener)
            accepted_event_type = self._resolve_accepted_event_type(listener.on_application_event)
            if accepted_event_type is None or isinstance(event, accepted_event_type):
                listener.on_application_event(event)

    def _get_application_listeners(self):
        for listener in self._app_listeners:
            yield listener
        for bean_name in self._app_listener_beans:
            listener = self._bean_factory.get_bean(bean_name, required_type=ApplicationEventListener)
            if listener is not None:
                yield listener

    def _resolve_accepted_event_type(self, method) -> Type[ApplicationEvent]:
        args_spec = inspect.getfullargspec(method)
        args = args_spec.args
        event_type_arg = None
        if len(args) > 0:
            if args[0] in ('self', 'cls'):
                if len(args) > 1:
                    event_type_arg = args[1]
            else:
                event_type_arg = args[0]
        if event_type_arg is not None:
            hints = args_spec.annotations
            return hints.get(event_type_arg)
