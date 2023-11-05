from rhazes.context import ApplicationContext
from rhazes.protocol import (
    BeanBuilderStrategy,
    BeanFactory,
    DependencyNode,
    DependencyNodeMetadata,
)
from rhazes.utils import synchronized


class DefaultBeanBuilderStrategy(BeanBuilderStrategy):
    def execute(self) -> object:
        args: list = self.metadata.args
        dependency_positions = self.metadata.dependency_position
        for dep in self.metadata.dependencies:
            lazy = (
                self.metadata.lazy_dependencies is not None
                and dep in self.metadata.lazy_dependencies
            )
            args[dependency_positions[dep]] = (
                ApplicationContext.get_lazy_bean(dep)
                if lazy
                else ApplicationContext.get_bean(dep)
            )
        if self.metadata.is_factory:
            factory: BeanFactory = self.node.cls(*self.metadata.args)
            return factory.produce()
        else:
            return self.node.cls(*self.metadata.args)


class SingletonBeanBuilderStrategy(DefaultBeanBuilderStrategy):
    def __init__(self, node: DependencyNode, metadata: DependencyNodeMetadata):
        super().__init__(node, metadata)
        self.instance = None

    @synchronized
    def execute(self) -> object:
        if self.instance is None:
            self.instance = super(SingletonBeanBuilderStrategy, self).execute()
        return self.instance
