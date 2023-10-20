import functools
from dataclasses import dataclass
from typing import Optional


@dataclass(unsafe_hash=True)
class BeanDetails:
    bean_for: Optional[type]
    primary: bool = False


def bean(_for=None, primary=False):
    def decorator(cls):
        if _for is not None and not issubclass(cls, _for):
            raise Exception(
                f"{cls} bean is meant to be registered for interface {_for} "
                f"but its not a subclass of that interface"
            )

        @functools.wraps(cls, updated=())
        class DecoratedBean(cls):
            @classmethod
            def bean_details(cls) -> BeanDetails:
                return BeanDetails(_for, primary)

        return DecoratedBean

    return decorator
