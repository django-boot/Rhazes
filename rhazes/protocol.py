from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from rhazes.decorator import BeanDetails


@runtime_checkable
class BeanProtocol(Protocol):
    @classmethod
    def bean_details(cls) -> BeanDetails:
        ...


class BeanFactory(ABC):
    @classmethod
    @abstractmethod
    def produces(cls):
        """
        Determines what type of object (class) this factory produces
        :return: class of which the object in factory method will be
        """
        pass

    @abstractmethod
    def produce(self):
        """
        :return: object of type from cls.produces()
        """
        pass
