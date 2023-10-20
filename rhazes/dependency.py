import inspect
import logging
from dataclasses import dataclass
from pydoc import locate
from typing import Set, List, Optional, Type, Dict, Iterable
import copy

from rhazes.collections.stack import UniqueStack
from rhazes.decorator import BeanDetails
from rhazes.exceptions import DependencyCycleException, MissingDependencyException
from rhazes.protocol import BeanProtocol

logger = logging.getLogger(__name__)


class DependencyNode:
    def __init__(self, cls):
        self.cls = cls
        self.dependencies = []

    def add_dependency(self, dependency: "DependencyNode"):
        self.dependencies.append(dependency)

    def __str__(self):
        return str(self.cls)


@dataclass
class DependencyNodeMetadata:
    """
    - dependencies: list of dependency classes
    - dependency_position: dictionary of dependency class positions in arguments
    - args: list of prefilled arguments to be used as *args for constructing
    """
    dependencies: list
    dependency_position: dict
    args: list
    bean_for: Optional[Type] = None

    @staticmethod
    def generate(cls: Type[BeanProtocol], bean_classes: Iterable[BeanProtocol], bean_interface_mapping: Dict[Type, Type]):
        """
        Generates DependencyNodeMetadata instance for a class (cls) after validating its constructor dependencies
        :param cls: class to generate DependencyNodeMetadata for
        :param bean_classes: other bean classes, possible to depend on
        :param bean_interface_mapping: possible classes to depend on
        :return: generated DependencyNodeMetadata
        """
        args = []
        dependencies = []
        dependency_position = {}
        signature = inspect.signature(cls.__init__)
        i = 0
        for k, v in signature.parameters.items():
            if k == "self":
                continue

            if k in ["args", "kwargs"]:
                logger.warning(
                    f"bean class {cls} has default __init__ which uses *args, **kwargs. "
                    f"It's impossible to detect the inputs"
                )
                continue

            clazz = None

            if type(v.annotation) == str:
                clazz = locate(f"{cls.__module__}.{v.annotation}")
                if clazz is None:
                    raise Exception(f"Failed to locate {v.annotation}")
            else:
                clazz = v.annotation

            if clazz in bean_classes:
                dependencies.append(clazz)
                args.append(None)
                dependency_position[clazz] = i
            elif clazz in bean_interface_mapping:
                dependencies.append(bean_interface_mapping[clazz])
                args.append(None)
                dependency_position[bean_interface_mapping[clazz]] = i
            elif v.default == v.empty:
                raise MissingDependencyException(cls, clazz)
            else:
                args.append(v.default)
            i += 1
        return DependencyNodeMetadata(dependencies, dependency_position, args, cls.bean_details().bean_for)


class DependencyResolver:

    def __init__(self, bean_classes: Set[Type[BeanProtocol]]):
        self.bean_classes: Set[Type[BeanProtocol]] = bean_classes
        self.bean_interface_map = {}
        self.fill_bean_interface_map()
        self.objects = {}
        self.node_registry = {}
        self.node_metadata_registry = {}

    def fill_bean_interface_map(self):
        # Map list of implementations (value) for each bean interface (value)
        for bean_class in self.bean_classes:
            if bean_class.bean_details().bean_for is not None:
                bean_classes = self.bean_interface_map.get(bean_class.bean_details().bean_for, [])
                bean_classes.append(bean_class)
                self.bean_interface_map[bean_class.bean_details().bean_for] = bean_classes

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

        # If the bean is presenting an interface then
        if cls.bean_details().bean_for is not None:
            self.node_registry[cls.bean_details().bean_for] = node

        return node

    def register_metadata(self, cls) -> DependencyNodeMetadata:
        """
        Creates DependencyNodeMetadata and registers it for the cls in self.node_metadata_registry
        :param cls: class to generate DependencyNodeMetadata for
        :return generated DependencyNodeMetadata
        """
        metadata = DependencyNodeMetadata.generate(cls, self.bean_classes, self.bean_interface_map)
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
        self.build(node)
        stack.pop()

    def build(self, node: DependencyNode):
        metadata: DependencyNodeMetadata = self.node_metadata_registry[node.cls]
        args: list = metadata.args
        dependency_positions = metadata.dependency_position
        for dep in metadata.dependencies:
            args[dependency_positions[dep]] = self.objects[dep]
        obj = node.cls(*metadata.args)
        self.objects[node.cls] = obj
        if metadata.bean_for is not None and node.cls == self.bean_interface_map[metadata.bean_for]:
            self.objects[metadata.bean_for] = obj

