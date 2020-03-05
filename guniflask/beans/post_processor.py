# coding=utf-8

__all__ = ['BeanPostProcessor']


class BeanPostProcessor:
    def post_process_before_instantiation(self, bean_type: type, bean_name: str):
        return None

    def post_process_after_initialization(self, bean, bean_name: str):
        return bean
