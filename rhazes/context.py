from rhazes.dependency import DependencyResolver
from rhazes.protocol import BeanProtocol, BeanFactory
from rhazes.registry import BeanRegistry
from rhazes.scanner import ModuleScanner, class_scanner


class ApplicationContext:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(ApplicationContext, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self._initialized = False
        self._module_scanner = ModuleScanner()
        self.beans = BeanRegistry()

    def _initialize_beans(self):
        beans = set()
        bean_factories = set()
        modules = self._module_scanner.scan()
        for module in modules:
            scanned_classes = class_scanner(module)
            for scanned_class in scanned_classes:
                if issubclass(scanned_class, (BeanProtocol,)):
                    beans.add(scanned_class)
                elif issubclass(scanned_class, (BeanFactory,)):
                    bean_factories.add(scanned_class)

        for cls, obj in DependencyResolver(beans, bean_factories).resolve().items():
            self.beans.register_bean(cls, obj)

    def initialize(self):
        if self._initialized:
            return
        self._initialize_beans()
        self._initialized = True
