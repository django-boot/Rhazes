from rhazes.decorator import service


class SomeABC:
    pass


@service(_for=SomeABC, primary=True)
class DepAI1(SomeABC):
    def __init__(self, dep_b: "DepB"):
        self.dep = dep_b


@service(_for=SomeABC)
class DepAI2(SomeABC):
    def __init__(self, dep_b: "DepB"):
        self.dep = dep_b


@service()
class DepB:
    def __init__(self, dep_c: "DepC"):
        self.dep = dep_c


@service()
class DepC:
    pass
