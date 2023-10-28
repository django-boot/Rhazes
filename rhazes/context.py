from typing import Optional, List

from django.conf import settings
from django.utils.functional import SimpleLazyObject

from rhazes.dependency import DependencyResolver
from rhazes.protocol import BeanProtocol
from rhazes.scanner import ModuleScanner, class_scanner


class ApplicationContext:
    _initialized = False
    _builder_registry = {}
    _additional_roots_to_scan = []

    @classmethod
    def get_roots_to_scan(cls):
        roots_to_scan = cls._roots_to_scan()
        return cls._additional_roots_to_scan + roots_to_scan

    @classmethod
    def _initialize_beans(cls):
        beans = set()
        modules = ModuleScanner(cls.get_roots_to_scan()).scan()
        for module in modules:
            scanned_classes = class_scanner(module)
            for scanned_class in scanned_classes:
                if issubclass(scanned_class, (BeanProtocol,)):
                    beans.add(scanned_class)

        for clazz, obj in DependencyResolver(beans).resolve().items():
            cls.register_bean(clazz, obj)

    @classmethod
    def _roots_to_scan(cls):
        if hasattr(settings, "RHAZES_PACKAGES"):
            return settings.RHAZES_PACKAGES
        return settings.INSTALLED_APPS

    @classmethod
    def initialize(cls, additional_roots_to_scan: List[str] = None):
        if additional_roots_to_scan is not None:
            cls._additional_roots_to_scan = additional_roots_to_scan

        if cls._initialized:
            return
        cls._initialize_beans()
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
        return SimpleLazyObject(lambda: cls.get_bean(of))
