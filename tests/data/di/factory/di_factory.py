from abc import ABC, abstractmethod

from rhazes.decorator import bean
from rhazes.protocol import BeanFactory


class SomeInterface(ABC):
    @abstractmethod
    def name(self):
        pass


@bean()
class TestStringGeneratorBean:
    def get_string(self):
        return "test"


@bean()
class SomeInterfaceFactory(BeanFactory):
    def __init__(self, tsg: TestStringGeneratorBean):
        self.tsg = tsg

    @classmethod
    def produces(cls):
        return SomeInterface

    def produce(self):
        factory = self

        class SomeInterfaceImpl(SomeInterface):
            def name(self):
                return factory.tsg.get_string()

        return SomeInterfaceImpl()
