# coding=utf-8

from typing import List, get_type_hints
import inspect
from functools import partial

from guniflask.beans.definition import BeanDefinition
from guniflask.beans.definition_registry import BeanDefinitionRegistry
from guniflask.beans.errors import BeanTypeNotDeclaredError, BeanTypeNotAllowedError, BeanNotOfRequiredTypeError, \
    BeanCreationError, NoUniqueBeanDefinitionError, BeansError
from guniflask.beans.post_processor import BeanPostProcessor
from guniflask.beans.bean_registry import SingletonBeanRegistry

__all__ = ['BeanFactory']


class BeanFactory(SingletonBeanRegistry, BeanDefinitionRegistry):

    def __init__(self):
        SingletonBeanRegistry.__init__(self)
        BeanDefinitionRegistry.__init__(self)
        self._bean_post_processors = []

    def get_bean(self, bean_name, required_type: type = None):
        bean = None

        share_instance = self.get_singleton(bean_name)
        if share_instance is not None:
            bean = share_instance
        else:
            bean_definition = self.get_bean_definition(bean_name)
            if bean_definition.is_singleton():
                bean = self.get_singleton_from_factory(bean_name,
                                                       partial(self._create_bean, bean_name, bean_definition))
            elif bean_definition.is_prototype():
                # TODO: support prototype
                pass

        # Check if required type matches the type of the actual bean instance.
        if bean is not None and required_type is not None:
            if not issubclass(type(bean), required_type):
                raise BeanNotOfRequiredTypeError(bean, required_type, type(bean))
        return bean

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

    def add_bean_post_processor(self, bean_post_processor: BeanPostProcessor):
        try:
            self._bean_post_processors.remove(bean_post_processor)
        except ValueError:
            pass
        self._bean_post_processors.append(bean_post_processor)

    @property
    def bean_post_processors(self) -> List[BeanPostProcessor]:
        return self._bean_post_processors

    def _create_bean(self, bean_name: str, bean_definition: BeanDefinition):
        bean = self._resolve_before_instantiation(bean_name, bean_definition)
        if bean is not None:
            return bean
        bean = self._do_create_bean(bean_name, bean_definition)
        return bean

    def _do_create_bean(self, bean_name: str, bean_definition: BeanDefinition):
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
            func = source.__init__
            real_func = source
        elif inspect.isfunction(source) or inspect.ismethod(source):
            if factory_bean is None:
                func = source
            else:
                func = getattr(factory_bean, source.__name__)
            real_func = source
        else:
            raise BeanCreationError(bean_name)

        arg_spec = inspect.getfullargspec(func)
        NO_VALUE = object()
        if len(arg_spec.args) > 0 and arg_spec.args[0] in ('self', 'cls'):
            args = list(arg_spec.args)[1:]
        else:
            args = list(arg_spec.args)
        if arg_spec.defaults is not None:
            args_value = [NO_VALUE] * (len(args) - len(arg_spec.defaults)) + list(arg_spec.defaults)
        else:
            args_value = [NO_VALUE] * len(args)
        if arg_spec.kwonlydefaults is not None:
            kwargs_value = dict(arg_spec)
        else:
            kwargs_value = dict()
        hints = dict(arg_spec.annotations)

        def resolve_arg(arg):
            bean = None
            required_type = hints.get(arg)
            if required_type is None:
                try:
                    bean = self.get_bean(arg)
                except BeansError:
                    pass
            else:
                candidates = self.get_beans_of_type(required_type)
                if len(candidates) == 1:
                    bean = list(candidates.values())[0]
                elif len(candidates) > 1:
                    if arg in candidates:
                        bean = candidates[arg]
                    else:
                        raise NoUniqueBeanDefinitionError(required_type)
            return bean

        for i, a in enumerate(args):
            v = resolve_arg(a)
            if v is not None:
                args_value[i] = v
        for a in list(kwargs_value.keys()):
            v = resolve_arg(a)
            if v is not None:
                kwargs_value[a] = v

        no_value_args = []
        for i, v in enumerate(args_value):
            if v == NO_VALUE:
                no_value_args.append(args[i])
        if len(no_value_args) > 0:
            raise BeanCreationError(bean_name, message='Cannot create bean named "{}", '
                                                       'because the following arguments cannot be resolved: '
                                                       '{}'.format(bean_name, ', '.join(no_value_args)))

        bean = real_func(*args_value, **kwargs_value)
        bean = self._apply_bean_post_processors_after_initialization(bean, bean_name)
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

    def _resolve_before_instantiation(self, bean_name, bean_definition: BeanDefinition):
        bean = None
        bean_type = self._resolve_bean_type(bean_name, bean_definition)
        if bean_type is not None:
            bean = self._apply_bean_post_processors_before_instantiation(bean_type, bean_name)
            if bean is not None:
                bean = self._apply_bean_post_processors_after_initialization(bean, bean_name)
        return bean

    def _apply_bean_post_processors_before_instantiation(self, bean_type: type, bean_name: str):
        for post_processor in self.bean_post_processors:
            result = post_processor.post_process_before_instantiation(bean_type, bean_name)
            if result is not None:
                return result

    def _apply_bean_post_processors_after_initialization(self, bean, bean_name: str):
        result = bean
        for post_processor in self.bean_post_processors:
            result = post_processor.post_process_after_initialization(bean, bean_name)
            if result is None:
                return result
        return result
