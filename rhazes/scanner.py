import importlib
import inspect
from typing import Optional, List, Set

from django.conf import settings


def class_scanner(module: str):
    result = []
    for _, cls in inspect.getmembers(importlib.import_module(module), inspect.isclass):
        if cls.__module__ == module:
            result.append(cls)
    return result


class ModuleScanner:
    """
    Scans for python packages submodules recursively
    """

    def __init__(self, roots_to_scan: Optional[List[str]] = None):
        self.roots_to_scan = (
            roots_to_scan if roots_to_scan is not None else self._roots_to_scan()
        )

    @classmethod
    def _roots_to_scan(cls):
        if hasattr(settings, "RHAZES_PACKAGES"):
            return settings.RHAZES_PACKAGES
        return settings.INSTALLED_APPS

    def _list_submodules(self, module) -> list[str]:
        """
        Args:
            module: The module to list submodules from.
        """
        # We first respect __all__ attribute if it already defined.
        submodules = getattr(module, "__all__", None)
        if submodules:
            return submodules

        # Then, we respect __init__.py file to get imported submodules.
        import inspect

        submodules = [
            o[0] for o in inspect.getmembers(module) if inspect.ismodule(o[1])
        ]
        if submodules:
            return submodules

        # Finally we can just scan for submodules via pkgutil.
        import pkgutil

        # pkgutill will invoke `importlib.machinery.all_suffixes()` to
        # determine whether a file is a module or not, so if you get
        # any submoudles that are unexpected to get, you need to check
        # this function to do the confirmation.
        # If you want to retrive a directory as a submoudle, you will
        # need to clarify this by putting a `__init__.py`` file in the
        # folder, even for Python3.
        if hasattr(module, "__path__"):
            return [x.name for x in pkgutil.iter_modules(module.__path__)]
        return []

    def scan(self) -> Set[str]:
        packages = set()
        for pkg in self.roots_to_scan:
            packages.update(self._scan(pkg))
        return packages

    def _scan(self, pkg) -> Set[str]:
        packages = set()
        try:
            mod = importlib.import_module(pkg)
            for item in self._list_submodules(mod):
                sub_m = f"{pkg}.{item}"
                packages.update(self._scan(sub_m))
            packages.add(pkg)
        except ModuleNotFoundError:
            pass
        return packages
