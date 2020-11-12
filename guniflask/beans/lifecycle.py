from abc import ABCMeta, abstractmethod


class InitializingBean(metaclass=ABCMeta):
    @abstractmethod
    def after_properties_set(self):
        pass  # pragma: no cover


class SmartInitializingSingleton(metaclass=ABCMeta):
    @abstractmethod
    def after_singletons_instantiated(self):
        pass  # pragma: no cover


class DisposableBean(metaclass=ABCMeta):
    @abstractmethod
    def destroy(self):
        pass  # pragma: no cover
