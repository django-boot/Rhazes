import inspect
from typing import List
import importlib
from pkgutil import iter_modules
from setuptools import find_packages


def class_scanner(module: str, selector=lambda x: True):
    result = []
    for _, cls in inspect.getmembers(importlib.import_module(module), inspect.isclass):
        if cls.__module__ == module and selector(cls):
            result.append(cls)
    return result


class ModuleScanner:
    """
    Scans for python packages submodules recursively
    """

    def __init__(self, roots_to_scan: List[str]):
        self.roots_to_scan = roots_to_scan

    def find_submodules(self, package, pkgpath):
        modules = set()
        for info in iter_modules([pkgpath]):
            if not info.ispkg:
                modules.add(package + "." + info.name)
        return modules

    def recurse_modules(self, package):
        modules = set()
        try:
            base_package_path = importlib.import_module(package).__path__[0]
        except ModuleNotFoundError:
            return modules
        modules.add(package)
        modules.update(self.find_submodules(package, base_package_path))
        for pkg in find_packages(base_package_path):
            modules.update(self.recurse_modules(f"{package}.{pkg}"))
        return modules

    def scan(self):
        modules = set()
        for package in self.roots_to_scan:
            modules.update(self.recurse_modules(package))
        return modules
