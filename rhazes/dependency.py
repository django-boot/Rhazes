from typing import Set, Type

from rhazes.collections.stack import UniqueStack
from rhazes.exceptions import DependencyCycleException
from rhazes.protocol import (
    BeanProtocol,
    BeanFactory,
    DependencyNodeMetadata,
    DependencyNode,
)


class NodeBuilder:
    def __init__(self, node: DependencyNode, metadata: DependencyNodeMetadata):
        self.node = node
        self.metadata = metadata

    def build(self, application_context):
        args: list = self.metadata.args
        dependency_positions = self.metadata.dependency_position
        for dep in self.metadata.dependencies:
            lazy = (
                self.metadata.lazy_dependencies is not None
                and dep in self.metadata.lazy_dependencies
            )
            args[dependency_positions[dep]] = (
                application_context.get_lazy_bean(dep)
                if lazy
                else application_context.get_bean(dep)
            )
        if self.metadata.is_factory:
            factory: BeanFactory = self.node.cls(*self.metadata.args)
            return factory.produce()
        else:
            return self.node.cls(*self.metadata.args)


class SingletonNodeBuilder:
    def __init__(self, builder: NodeBuilder):
        self.builder = builder
        self.instance = None

    def build(self, application_context):
        if self.instance is not None:
            return self.instance
        self.instance = self.builder.build(application_context)
        return self.instance


class DependencyResolver:
    def __init__(self, bean_classes: Set[Type[BeanProtocol]] = None):
        self.bean_classes: Set[Type[BeanProtocol]] = (
            bean_classes if bean_classes is not None else set()
        )
        self.bean_interface_map = {}
        self.fill_bean_interface_map()
        self.objects = {}
        self.node_registry = {}
        self.node_metadata_registry = {}

    def __add_or_init_interface_mapping(self, interface, cls):
        mapping = self.bean_interface_map.get(interface, [])
        mapping.append(cls)
        self.bean_interface_map[interface] = mapping

    def fill_bean_interface_map(self):
        # Map list of implementations (value) for each bean interface (value)
        for bean_class in self.bean_classes:
            if bean_class.bean_details().bean_for is not None:
                self.__add_or_init_interface_mapping(
                    bean_class.bean_details().bean_for, bean_class
                )

        # Find primary implementation of each interface and update the map
        for bean_for, implementations in self.bean_interface_map.items():
            primary = implementations[0]
            if len(implementations) > 1:
                for implementation in implementations:
                    if implementation.bean_details().primary:
                        primary = implementation
                        break
            self.bean_interface_map[bean_for] = primary

    def register_dependency_node(self, cls) -> DependencyNode:

        # If the dependency is not a bean (it could be the interface of another bean) then look for implementation bean
        if cls in self.bean_interface_map:
            return self.register_dependency_node(self.bean_interface_map[cls])

        # If we have already created DependencyNode for this class then return it
        if cls in self.node_registry:
            return self.node_registry[cls]
        node = DependencyNode(cls)
        self.node_registry[cls] = node

        # If the bean is presenting an interface then register it for that interface too
        if issubclass(cls, (BeanProtocol,)) and cls.bean_details().bean_for is not None:
            self.node_registry[cls.bean_details().bean_for] = node

        return node

    def register_metadata(self, cls) -> DependencyNodeMetadata:
        """
        Creates DependencyNodeMetadata and registers it for the cls in self.node_metadata_registry
        :param cls: class to generate DependencyNodeMetadata for
        :return generated DependencyNodeMetadata
        """
        metadata = DependencyNodeMetadata.generate(
            cls, self.bean_classes, self.bean_interface_map
        )
        self.node_metadata_registry[cls] = metadata
        return metadata

    def resolve(self) -> dict:
        """
        Resolves dependencies by building graph, traverse it and returning list of created objects
        :returns dictionary of created objects for each class
        """

        to_process = []

        # Building Graph
        for cls in self.bean_classes:
            metadata = self.register_metadata(cls)
            node = self.register_dependency_node(cls)
            for dependency in metadata.dependencies:
                node.add_dependency(self.register_dependency_node(dependency))
            to_process.append(node)

        # Processing each node
        for node in to_process:
            self._process(node, UniqueStack())

        return self.objects

    def _process(self, node, stack):
        """
        Depth first traversal on nodes.
            Base case: node is already built, so we ignore building again
            Using "post-order" BFS to use a UniqueStack in order to detect cycles

        Accepts any node and if its already processed ignores it.
        The reason is that we aren't sure we have a single dependency tree or graph or multiple ones
        That's why this method is called for all bean classes

        :param node: a node to start processing from
        :param stack: instance of UniqueStack for dependency cycle detection
        :return:
        """
        if node.cls in self.objects:
            return
        try:
            stack.append(node)
        except ValueError:  # item is not unique in the stack
            raise DependencyCycleException(stack, node)
        for child in node.dependencies:
            self._process(child, stack)
        self.generate_builder(node)
        stack.pop()

    def generate_builder(self, node: DependencyNode):
        metadata: DependencyNodeMetadata = self.node_metadata_registry[node.cls]

        if metadata.is_factory:
            clazz = metadata.bean_for
        else:
            clazz = node.cls

        node_builder = NodeBuilder(node, metadata)
        if metadata.is_singleton:
            node_builder = SingletonNodeBuilder(node_builder)

        self.objects[clazz] = node_builder.build
        if metadata.bean_for is not None and (
            metadata.is_factory
            or node.cls == self.bean_interface_map[metadata.bean_for]
        ):
            self.objects[metadata.bean_for] = node_builder.build
