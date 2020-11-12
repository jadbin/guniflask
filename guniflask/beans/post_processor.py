from typing import Any


class BeanPostProcessor:
    def post_process_before_instantiation(self, bean_type: type, bean_name: str):
        return None

    def post_process_before_initialization(self, bean: Any, bean_name: str) -> Any:
        return bean

    def post_process_after_initialization(self, bean: Any, bean_name: str) -> Any:
        return bean
