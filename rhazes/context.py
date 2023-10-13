from rhazes.initializer import BeanInitializer
from rhazes.registry import BeanRegistry
from rhazes.scanner import ModuleScanner


class ApplicationContext(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ApplicationContext, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.__initialized = False
        self.__module_scanner = ModuleScanner()
        self.beans = BeanRegistry()

    def initialize(self):
        if self.__initialized:
            return
        BeanInitializer(
            self.__module_scanner.scan(),
            self.beans
        )
        self.__initialized = True
