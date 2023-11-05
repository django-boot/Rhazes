from abc import ABC

from rhazes.decorator import bean
from rhazes.scope import Scope


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
    def __init__(self, dep_c: DepCInterface, dep_d: "DepD"):
        self.dep_c = dep_c
        self.dep_d = dep_d


@bean(_for=DepCInterface, primary=True, scope=Scope.SINGLETON)
class DepC(DepCInterface):
    pass


@bean(_for=DepCInterface, primary=False)
class DepCImp2(DepCInterface):
    pass


@bean()
class DepD:
    def name(self):
        return "DepD"


@bean(lazy_dependencies=[DepD])
class DepE:
    def __init__(self, dep_d: DepD):
        self.dep_d = dep_d
