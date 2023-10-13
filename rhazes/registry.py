from typing import Optional

from rhazes.decorator import ServiceDetails


class BeanRegistry:
    def __init__(self):
        self._registry = {}

    def _register(self, cls, obj, primary: bool):
        if cls not in self._registry or primary:
            self._registry[cls] = obj

    def register_service(self, cls, obj, override=False):
        service_details: ServiceDetails = getattr(obj, "service_details")()
        self._register(cls, obj, service_details.primary)
        if (
            service_details.service_for is not None
            and service_details.service_for != cls
        ):
            self._register(
                service_details.service_for, obj, service_details.primary or override
            )

    def get_bean(self, of: type) -> Optional[object]:
        return self._registry.get(of)
