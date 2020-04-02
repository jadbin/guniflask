# coding=utf-8

from typing import List, get_type_hints
import inspect
from functools import partial
from abc import ABCMeta, abstractmethod

from guniflask.beans.post_processor import BeanPostProcessor
from guniflask.beans.definition import BeanDefinition
from guniflask.beans.definition_registry import BeanDefinitionRegistry
from guniflask.beans.errors import BeanTypeNotDeclaredError, BeanTypeNotAllowedError, BeanCreationError, \
    BeanNotOfRequiredTypeError, NoUniqueBeanDefinitionError
from guniflask.beans.factory_hook import InitializingBean, SmartInitializingSingleton, DisposableBean
from guniflask.beans.constructor_resolver import ConstructorResolver
from guniflask.beans.factory import BeanFactoryAware, BeanNameAware, ConfigurableBeanFactory
from guniflask.beans.errors import NoSuchBeanDefinitionError, BeanDefinitionStoreError

__all__ = ['AbstractBeanFactory',
           'DefaultBeanFactory']


class AbstractBeanFactory(ConfigurableBeanFactory, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
        self._bean_post_processors = []

    def add_bean_post_processor(self, bean_post_processor: BeanPostProcessor):
        try:
            self._bean_post_processors.remove(bean_post_processor)
        except ValueError:
            pass
        self._bean_post_processors.append(bean_post_processor)

    @property
    def bean_post_processors(self) -> List[BeanPostProcessor]:
        return self._bean_post_processors

    def get_bean(self, bean_name, required_type: type = None):
        bean = None

        share_instance = self.get_singleton(bean_name)
        if share_instance is not None:
            bean = share_instance
        else:
            bean_definition = self.get_bean_definition(bean_name)
            if bean_definition.is_singleton():
                bean = self.get_singleton_from_factory(bean_name,
                                                       partial(self.create_bean, bean_name, bean_definition))
            elif bean_definition.is_prototype():
                # TODO: support prototype
                pass

        # Check if required type matches the type of the actual bean instance.
        if bean is not None and required_type is not None:
            if not issubclass(type(bean), required_type):
                raise BeanNotOfRequiredTypeError(bean, required_type, type(bean))
        return bean

    def get_bean_of_type(self, required_type: type):
        candidates = self.get_beans_of_type(required_type)
        if len(candidates) == 1:
            return list(candidates.values())[0]
        if len(candidates) > 1:
            raise NoUniqueBeanDefinitionError(required_type)

    def get_beans_of_type(self, required_type: type):
        names = self.get_bean_names_for_type(required_type)
        result = {}
        for name in names:
            bean = self.get_bean(name, required_type=required_type)
            result[name] = bean
        return result

    def is_type_match(self, bean_name: str, type_to_match: type) -> bool:
        bean = self.get_singleton(bean_name)
        if bean is not None:
            return isinstance(bean, type_to_match)
        if not self.contains_bean_definition(bean_name):
            return False
        bean_type = self._resolve_bean_type(bean_name, self.get_bean_definition(bean_name))
        if bean_type is None:
            return False
        return issubclass(bean_type, type_to_match)

    def _resolve_bean_type(self, bean_name: str, bean_definition: BeanDefinition) -> type:
        source = bean_definition.source
        if inspect.isclass(source):
            return source
        if inspect.isfunction(source) or inspect.ismethod(source):
            hints = get_type_hints(source)
            if 'return' not in hints:
                raise BeanTypeNotDeclaredError(bean_name)
            bean_type = hints['return']
            if not inspect.isclass(bean_type):
                raise BeanTypeNotAllowedError(bean_name, bean_type)
            return bean_type

    @abstractmethod
    def create_bean(self, bean_name: str, bean_definition: BeanDefinition):
        pass

    @abstractmethod
    def contains_bean_definition(self, bean_name: str) -> bool:
        pass

    @abstractmethod
    def get_bean_definition(self, bean_name: str) -> BeanDefinition:
        pass


class DefaultBeanFactory(AbstractBeanFactory, BeanDefinitionRegistry):
    def __init__(self):
        AbstractBeanFactory.__init__(self)
        self._constructor_resolver = ConstructorResolver(self)
        self._bean_definition_map = {}
        self._allow_bean_definition_overriding = True

    def get_bean_names_for_type(self, required_type: type) -> List[str]:
        names = []
        for bean_name in self._bean_definition_map:
            if self.is_type_match(bean_name, required_type):
                names.append(bean_name)
        return names

    def pre_instantiate_singletons(self):
        bean_names = self.get_bean_definition_names()
        for bean_name in bean_names:
            bean_definition = self.get_bean_definition(bean_name)
            if bean_definition.is_singleton():
                self.get_bean(bean_name)

        for bean_name in bean_names:
            singleton = self.get_singleton(bean_name)
            if isinstance(singleton, SmartInitializingSingleton):
                singleton.after_singletons_instantiated()

    def create_bean(self, bean_name: str, bean_definition: BeanDefinition):
        bean = self._resolve_before_instantiation(bean_name, bean_definition)
        if bean is not None:
            return bean
        bean = self._do_create_bean(bean_name, bean_definition)
        return bean

    def _do_create_bean(self, bean_name: str, bean_definition: BeanDefinition):
        bean = self._create_bean_instance(bean_name, bean_definition)
        bean = self._initialize_bean(bean, bean_name)
        self._register_disposable_bean_if_necessary(bean_name, bean, bean_definition)
        return bean

    def _create_bean_instance(self, bean_name: str, bean_definition: BeanDefinition):
        """
        1. Find the bean with the same name as arg if the required bean type is missing.
        2. Find beans which matches the required bean type.
        3. If there is only one matched bean, set it to arg.
        4. If there are more than one matched beans, choose the bean which has the same name with arg.
           Raise error if no such bean.
        5. Set arg to its declared default value.
        6. Raise error if there is any unassigned arg.

        Note: self and cls are special.
        """
        source = bean_definition.source
        factory_bean = None
        if bean_definition.factory_bean_name is not None:
            factory_bean = self.get_bean(bean_definition.factory_bean_name)
        if inspect.isclass(source):
            func = source
        elif inspect.isfunction(source) or inspect.ismethod(source):
            if factory_bean is None:
                func = source
            else:
                func = getattr(factory_bean, source.__name__)
        else:
            raise BeanCreationError(bean_name)
        try:
            bean = self._constructor_resolver.instantiate(func)
        except Exception as e:
            raise BeanCreationError(bean_name, message='Cannot create bean named "{}"\n{}'.format(bean_name, e))
        return bean

    def _resolve_bean_type(self, bean_name: str, bean_definition: BeanDefinition) -> type:
        source = bean_definition.source
        if inspect.isclass(source):
            return source
        if inspect.isfunction(source) or inspect.ismethod(source):
            hints = get_type_hints(source)
            if 'return' not in hints:
                raise BeanTypeNotDeclaredError(bean_name)
            bean_type = hints['return']
            if not inspect.isclass(bean_type):
                raise BeanTypeNotAllowedError(bean_name, bean_type)
            return bean_type

    def _resolve_before_instantiation(self, bean_name: str, bean_definition: BeanDefinition):
        bean = None
        bean_type = self._resolve_bean_type(bean_name, bean_definition)
        if bean_type is not None:
            bean = self._apply_bean_post_processors_before_instantiation(bean_type, bean_name)
            if bean is not None:
                bean = self._apply_bean_post_processors_after_initialization(bean, bean_name)
        return bean

    def _initialize_bean(self, bean, bean_name: str):
        self._invoke_aware_methods(bean, bean_name)
        wrapped_bean = bean
        wrapped_bean = self._apply_bean_post_processors_before_initialization(wrapped_bean, bean_name)
        self._invoke_init_methods(wrapped_bean)
        wrapped_bean = self._apply_bean_post_processors_after_initialization(wrapped_bean, bean_name)
        return wrapped_bean

    def _invoke_aware_methods(self, bean, bean_name: str):
        if isinstance(bean, BeanNameAware):
            bean.set_bean_name(bean_name)
        if isinstance(bean, BeanFactoryAware):
            bean.set_bean_factory(self)

    def _invoke_init_methods(self, bean):
        if isinstance(bean, InitializingBean):
            bean.after_properties_set()

    def _apply_bean_post_processors_before_instantiation(self, bean_type: type, bean_name: str):
        for post_processor in self.bean_post_processors:
            result = post_processor.post_process_before_instantiation(bean_type, bean_name)
            if result is not None:
                return result

    def _apply_bean_post_processors_before_initialization(self, bean, bean_name: str):
        for post_processor in self.bean_post_processors:
            result = post_processor.post_process_before_initialization(bean, bean_name)
            if result is not None:
                bean = result
        return bean

    def _apply_bean_post_processors_after_initialization(self, bean, bean_name: str):
        for post_processor in self.bean_post_processors:
            result = post_processor.post_process_after_initialization(bean, bean_name)
            if result is not None:
                bean = result
        return bean

    def _register_disposable_bean_if_necessary(self, bean_name: str, bean, bean_definition: BeanDefinition):
        if bean_definition.is_singleton() and isinstance(bean, DisposableBean):
            self.register_disposable_bean(bean_name, bean)

    def set_allow_bean_definition_overriding(self, allow_bean_definition_overriding: bool):
        self._allow_bean_definition_overriding = allow_bean_definition_overriding

    @property
    def is_allow_bean_definition_overriding(self) -> bool:
        return self._allow_bean_definition_overriding

    def register_bean_definition(self, bean_name: str, bean_definition: BeanDefinition):
        old_bean_definition = self._bean_definition_map.get(bean_name)
        if old_bean_definition is not None:
            if not self.is_allow_bean_definition_overriding:
                raise BeanDefinitionStoreError('A bean named "{}" is already bound'.format(bean_name))
        self._bean_definition_map[bean_name] = bean_definition

    def get_bean_definition(self, bean_name: str) -> BeanDefinition:
        bean_definition = self._bean_definition_map.get(bean_name)
        if bean_definition is None:
            raise NoSuchBeanDefinitionError(bean_name)
        return bean_definition

    def get_bean_definition_names(self) -> List[str]:
        return list(self._bean_definition_map.keys())

    def contains_bean_definition(self, bean_name: str) -> bool:
        return bean_name in self._bean_definition_map

    def remove_bean_definition(self, bean_name: str):
        if bean_name not in self._bean_definition_map:
            raise NoSuchBeanDefinitionError(bean_name)
        self._bean_definition_map.pop(bean_name)
