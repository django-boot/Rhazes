from typing import Optional, List


from rhazes.dependency import DependencyResolver
from rhazes.protocol import BeanProtocol
from rhazes.scanner import ModuleScanner, class_scanner
from rhazes.utils import LazyObject


class ApplicationContext:
    _initialized = False
    _builder_registry = {}

    @classmethod
    def _initialize_beans(cls, packages_to_scan: List[str]):
        beans = set()
        modules = ModuleScanner(packages_to_scan).scan()
        for module in modules:
            for bean in class_scanner(
                module, lambda clz: issubclass(clz, (BeanProtocol,))
            ):
                beans.add(bean)

        for clazz, obj in DependencyResolver(beans).resolve().items():
            cls.register_bean(clazz, obj)

    @classmethod
    def initialize(cls, packages_to_scan: List[str]):
        if packages_to_scan is not None:
            cls.packages_to_scan = packages_to_scan

        if cls._initialized:
            return
        cls._initialize_beans(packages_to_scan)
        cls._initialized = True

    @classmethod
    def register_bean(cls, clazz, builder, override=False):
        if clazz not in cls._builder_registry or override:
            cls._builder_registry[clazz] = builder

    @classmethod
    def get_bean(cls, of: type) -> Optional:
        builder = cls._builder_registry.get(of)
        if builder is None:
            return None
        return builder(cls)

    @classmethod
    def get_lazy_bean(cls, of: type) -> Optional:
        return LazyObject(lambda: cls.get_bean(of))
