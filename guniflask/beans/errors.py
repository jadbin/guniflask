# coding=utf-8

__all__ = ['BeansError',
           'NoSuchBeanDefinitionError', 'NoUniqueBeanDefinitionError',
           'BeanDefinitionStoreError',
           'BeanCreationError', 'BeanCurrentlyInCreationError',
           'BeanNotOfRequiredTypeError',
           'BeanTypeNotDeclaredError', 'BeanTypeNotAllowedError']


class BeansError(Exception):
    pass


class NoSuchBeanDefinitionError(BeansError):
    def __init__(self, bean_name):
        self.bean_name = bean_name
        super().__init__('No bean named "{}" available'.format(bean_name))


class NoUniqueBeanDefinitionError(BeansError):
    def __init__(self, bean_type):
        self.bean_type = bean_type
        super().__init__('"{}" is not a unique bean type'.format(bean_type))


class BeanDefinitionStoreError(BeansError):
    pass


class BeanCreationError(BeansError):
    def __init__(self, bean_name, message=None):
        self.bean_name = bean_name
        super().__init__(message or 'Error creating bean with name "{}"'.format(bean_name))


class BeanCurrentlyInCreationError(BeanCreationError):
    def __init__(self, bean_name):
        super().__init__(bean_name, message='Bean named "{}" is currently in creation: '
                                            'Is there an unresolvable circular reference?"'.format(bean_name))


class BeanNotOfRequiredTypeError(BeansError):
    def __init__(self, bean_name, required_type, actual_type):
        self.bean_name = bean_name
        self.required_type = required_type
        self.actual_type = actual_type
        super().__init__('Bean named "{}" is expected to be of type "{}"'
                         ' but was actually of type {}'.format(bean_name, required_type, actual_type))


class BeanTypeNotDeclaredError(BeansError):
    def __init__(self, bean_name):
        self.bean_name = bean_name
        super().__init__('The type of bean named "{}" is not declared'.format(bean_name))


class BeanTypeNotAllowedError(BeansError):
    def __init__(self, bean_name, bean_type):
        self.bean_name = bean_name
        self.bean_type = bean_type
        super().__init__('The type "{}" of bean named "{}" is not a allowed'.format(bean_type, bean_name))
