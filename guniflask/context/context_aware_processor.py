# coding=utf-8

from guniflask.beans.post_processor import BeanPostProcessorAdapter
from guniflask.context.bean_context import BeanContext, BeanContextAware

__all__ = ['BeanContextAwareProcessor']


class BeanContextAwareProcessor(BeanPostProcessorAdapter):
    def __init__(self, bean_context: BeanContext):
        self._bean_context = bean_context

    def post_process_before_initialization(self, bean, bean_name: str):
        if isinstance(bean, BeanContextAware):
            bean.set_bean_context(self._bean_context)
