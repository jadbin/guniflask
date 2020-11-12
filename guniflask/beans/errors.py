class BeansError(Exception):
    pass


class NoSuchBeanDefinitionError(BeansError):
    def __init__(self, bean_name):
        self.bean_name = bean_name
        super().__init__(f'No bean named "{bean_name}" available')


class NoUniqueBeanDefinitionError(BeansError):
    def __init__(self, bean_type):
        self.bean_type = bean_type
        super().__init__(f'"{bean_type}" is not a unique bean type')


class BeanDefinitionStoreError(BeansError):
    pass


class BeanCreationError(BeansError):
    def __init__(self, bean_name, message=None):
        self.bean_name = bean_name
        super().__init__(message or f'Error creating bean with name "{bean_name}"')


class BeanCurrentlyInCreationError(BeanCreationError):
    def __init__(self, bean_name):
        super().__init__(bean_name, message=f'Bean named "{bean_name}" is currently in creation: '
                                            'Is there an unresolvable circular reference?"')


class BeanNotOfRequiredTypeError(BeansError):
    def __init__(self, bean_name, required_type, actual_type):
        self.bean_name = bean_name
        self.required_type = required_type
        self.actual_type = actual_type
        super().__init__(f'Bean named "{bean_name}" is expected to be of type "{required_type}"'
                         f' but was actually of type {actual_type}')


class BeanTypeNotDeclaredError(BeansError):
    def __init__(self, bean_name):
        self.bean_name = bean_name
        super().__init__(f'The type of bean named "{bean_name}" is not declared')


class BeanTypeNotAllowedError(BeansError):
    def __init__(self, bean_name, bean_type):
        self.bean_name = bean_name
        self.bean_type = bean_type
        super().__init__(f'The type "{bean_type}" of bean named "{bean_name}" is not a allowed')
