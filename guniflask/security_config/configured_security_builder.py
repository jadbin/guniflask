from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Type, List, Any, Optional

from guniflask.security_config.security_builder import AbstractSecurityBuilder
from guniflask.security_config.security_configurer import SecurityConfigurer


class ConfiguredSecurityBuilder(AbstractSecurityBuilder, metaclass=ABCMeta):
    def __init__(self):
        AbstractSecurityBuilder.__init__(self)
        self._configurers = defaultdict(list)
        self._shared_objects = {}

    def get_configurers(self, configurer_type: Type[SecurityConfigurer]) -> List[SecurityConfigurer]:
        return self._configurers[configurer_type]

    def get_configurer(self, configurer_type: Type[SecurityConfigurer]) -> Optional[SecurityConfigurer]:
        configurers = self._configurers.get(configurer_type)
        if not configurers:
            return
        if len(configurers) != 1:
            raise ValueError(f'Only one configurer excepted for type {configurer_type.__name__}, '
                             f'but got {len(configurers)}')
        return configurers[0]

    def apply(self, configurer: SecurityConfigurer):
        configurer.builder = self
        self._add(configurer)
        return configurer

    def set_shared_object(self, shared_type: Type[Any], obj: Any):
        self._shared_objects[shared_type] = obj

    def get_shared_object(self, shared_type: Type[Any]) -> Any:
        return self._shared_objects.get(shared_type)

    def get_shared_objects(self):
        return self._shared_objects

    @abstractmethod
    def _perform_build(self) -> Any:
        pass  # pragma: no cover

    def _do_build(self) -> Any:
        self._before_init()
        self._init()

        self._before_configure()
        self._configure()

        result = self._perform_build()
        return result

    def _before_init(self):
        pass

    def _before_configure(self):
        pass

    def _init(self):
        configurers = self._get_all_configurers()
        for c in configurers:
            c.init(self)

    def _configure(self):
        configurers = self._get_all_configurers()
        for c in configurers:
            c.configure(self)

    def _get_all_configurers(self) -> List[SecurityConfigurer]:
        result = []
        for vlist in self._configurers.values():
            for v in vlist:
                result.append(v)
        return result

    def _add(self, configurer: SecurityConfigurer):
        cls = type(configurer)
        self._configurers[cls].append(configurer)
