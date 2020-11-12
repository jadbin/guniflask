from guniflask.beans.post_processor import BeanPostProcessor
from guniflask.context.bean_context import BeanContext, BeanContextAware


class BeanContextAwareProcessor(BeanPostProcessor):
    def __init__(self, bean_context: BeanContext):
        self._bean_context = bean_context

    def post_process_before_initialization(self, bean, bean_name: str):
        if isinstance(bean, BeanContextAware):
            bean.set_bean_context(self._bean_context)
