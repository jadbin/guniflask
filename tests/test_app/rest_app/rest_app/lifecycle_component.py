from guniflask.beans import InitializingBean, SmartInitializingSingleton, DisposableBean
from guniflask.context import component


@component
class LifecycleComponent(InitializingBean, SmartInitializingSingleton, DisposableBean):

    def after_properties_set(self):
        pass

    def after_singletons_instantiated(self):
        pass

    def destroy(self):
        pass
