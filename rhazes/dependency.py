import inspect
from pydoc import locate
from rhazes.collections.stack import UniqueStack
from rhazes.exceptions import DependencyCycleException, MissingDependencyException
import logging


logger = logging.getLogger(__name__)


class DependencyNode:
    def __init__(self, cls):
        self.cls = cls
        self.dependencies = []

    def add_dependency(self, dependency: "DependencyNode"):
        self.dependencies.append(dependency)

    def __str__(self):
        return str(self.cls)


class DependencyProcessor:

    def __init__(self, all_classes: set):
        self.all_classes = all_classes
        self.objects = {}
        self.node_registry = {}
        self.node_metadata_registry = {}

    def register_node(self, cls) -> DependencyNode:
        if cls in self.node_registry:
            return self.node_registry[cls]
        node = DependencyNode(cls)
        self.node_registry[cls] = node
        return node

    def register_metadata(self, cls):
        """

        :param cls: class to get arguments of
        :return: tuple:
            - dependencies: list of dependency classes
            - dependency_position: dictionary of dependency class positions in arguments
            - args: list of prefilled arguments to be used as *args for constructing
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
                logger.warning(f"Service class {cls} has default __init__ which uses *args, **kwargs. "
                               f"It's impossible to detect the inputs")
                continue

            clazz = None

            if type(v.annotation) == str:
                clazz = locate(f"{cls.__module__}.{v.annotation}")
                if clazz is None:
                    raise Exception(f"Failed to locate {v.annotation}")
            else:
                clazz = v.annotation

            if clazz in self.all_classes:
                dependencies.append(clazz)
                args.append(None)
                dependency_position[clazz] = i
            elif v.default == v.empty:
                raise MissingDependencyException(cls, clazz)  # Todo: depends on a object that is not in service classes
            else:
                args.append(v.default)
            i += 1
        self.node_metadata_registry[cls] = {
            "dependencies": dependencies,
            "dependency_position": dependency_position,
            "args": args,
        }
        return dependencies

    def process(self):
        to_process = []

        # Building Graph
        for cls in self.all_classes:
            dependencies = self.register_metadata(cls)
            node = self.register_node(cls)
            for dependency in dependencies:
                node.add_dependency(self.register_node(dependency))
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
        That's why this method is called for all service classes

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
        metadata = self.node_metadata_registry[node.cls]
        args: list = metadata["args"]
        dependency_positions = metadata["dependency_position"]
        for dep in metadata["dependencies"]:
            args[dependency_positions[dep]] = self.objects[dep]
        obj = node.cls(*metadata["args"])
        self.objects[node.cls] = obj
