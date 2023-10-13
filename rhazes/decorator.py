import functools
from dataclasses import dataclass
from typing import Optional


@dataclass(unsafe_hash=True)
class ServiceDetails:
    service_for: Optional[type]
    primary: bool = False


def service(_for=None, primary=False):
    def decorator(cls):
        if _for is not None and not issubclass(cls, _for):
            raise Exception(
                f"{cls} service is meant to be registered for interface {_for} "
                f"but its not a subclass of that interface"
            )

        @functools.wraps(cls, updated=())
        class DecoratedService(cls):
            @classmethod
            def service_details(cls) -> ServiceDetails:
                return ServiceDetails(_for, primary)

        return DecoratedService

    return decorator
