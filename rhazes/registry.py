from typing import Optional


class BeanRegistry:
    def __init__(self):
        self._registry = {}

    def register_bean(self, cls, obj, override=False):
        if cls not in self._registry or override:
            self._registry[cls] = obj

    def get_bean(self, of: type) -> Optional[object]:
        return self._registry.get(of)
