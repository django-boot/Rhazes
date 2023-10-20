from typing import Protocol

from rhazes.decorator import BeanDetails


class BeanProtocol(Protocol):
    @classmethod
    def bean_details(cls) -> BeanDetails:
        ...
