from rhazes.decorator import bean


@bean()
class DepA:
    def __init__(self, dep_b: "DepB"):
        self.dep = dep_b


@bean()
class DepB:
    def __init__(self, dep_c: "DepC"):
        self.dep = dep_c


@bean()
class DepC:
    def __init__(self, dep_a: "DepA"):
        self.dep = dep_a
