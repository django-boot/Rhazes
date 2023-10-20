from abc import ABC

from rhazes.decorator import bean


class SomeABC:
    pass


@bean(_for=SomeABC, primary=True)
class DepAI1(SomeABC):
    def __init__(self, dep_b: "DepB"):
        self.dep = dep_b


@bean(_for=SomeABC)
class DepAI2(SomeABC):
    def __init__(self, dep_b: "DepB"):
        self.dep = dep_b


class DepCInterface(ABC):
    pass


@bean()
class DepB:
    def __init__(self, dep_c: DepCInterface):
        self.dep = dep_c


@bean(_for=DepCInterface)
class DepC(DepCInterface):
    pass
