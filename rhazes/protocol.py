import inspect
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pydoc import locate
from typing import (
    Protocol,
    runtime_checkable,
    Optional,
    Iterable,
    Dict,
    Type,
    TypedDict,
    List,
)

from rhazes.exceptions import MissingDependencyException

logger = logging.getLogger(__name__)


@dataclass(unsafe_hash=True)
class BeanDetails:
    bean_for: Optional[type]
    primary: bool = False
    singleton: bool = False
    lazy_dependencies: Optional[List[type]] = None


@runtime_checkable
class BeanProtocol(Protocol):
    @classmethod
    def bean_details(cls) -> BeanDetails:
        ...


class BeanFactory(ABC):
    @classmethod
    def produces(cls):
        """
        Determines what type of object (class) this factory produces
        :return: class of which the object in factory method will be
        """
        if issubclass(cls, (BeanProtocol,)) and cls.bean_details().bean_for is not None:
            return cls.bean_details().bean_for
        raise NotImplementedError

    @abstractmethod
    def produce(self):
        """
        :return: object of type from cls.produces()
        """
        pass


@dataclass
class DependencyNodeMetadata:
    """
    - dependencies: list of dependency classes
    - dependency_position: dictionary of dependency class positions in arguments
    - args: list of prefilled arguments to be used as *args for constructing
    """

    dependencies: Optional[list]
    dependency_position: Optional[dict]
    args: Optional[list]
    bean_for: Optional[Type] = None
    is_factory: bool = False
    is_singleton: bool = False
    lazy_dependencies: Optional[list] = None

    @staticmethod
    def generate(
        cls,
        bean_classes: Iterable[BeanProtocol],
        bean_interface_mapping: Dict[Type, Type],
    ):
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
                    f"bean class {cls} has __init__ which uses *args or **kwargs. "
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

        bean_for = None
        is_factory = False
        is_singleton = False
        lazy_dependencies = None

        if issubclass(cls, (BeanProtocol,)):
            bean_for = cls.bean_details().bean_for
            is_singleton = cls.bean_details().singleton
            lazy_dependencies = cls.bean_details().lazy_dependencies
        if issubclass(cls, (BeanFactory,)):
            bean_for = bean_for if bean_for is not None else cls.produces()
            is_factory = True

        return DependencyNodeMetadata(
            dependencies,
            dependency_position,
            args,
            bean_for,
            is_factory,
            is_singleton,
            lazy_dependencies,
        )


class DependencyNode:
    def __init__(self, cls):
        self.cls = cls
        self.dependencies = []

    def add_dependency(self, dependency: "DependencyNode"):
        self.dependencies.append(dependency)

    def __str__(self):
        return str(self.cls)


class InjectionConfiguration(TypedDict):
    lazy: bool
