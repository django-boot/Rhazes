from typing import Set

from rhazes.initializer.dependency import DependencyProcessor
from rhazes.registry import BeanRegistry
from rhazes.scanner import class_scanner


def is_service_class(cls):
    return hasattr(cls, "service_details") and callable(cls.service_details)


class BeanInitializer:

    def __init__(self, modules: Set[str], registry: BeanRegistry):
        self.modules = modules
        self.registry = registry
        self._waiting_for = {}
        self.classes = set()

    def initialize(self):
        for module in self.modules:
            self.classes.update(
                class_scanner(module)
            )
        self.classes = [cls for cls in self.classes if is_service_class(cls)]
        dependency_manager = DependencyProcessor(self.classes)
        objects = dependency_manager.process()

        for cls, _object in objects.items():
            self.registry.register_service(cls, _object)

