class DepA:
    def __init__(self, dep_b: "DepB"):
        self.dep = dep_b


class DepB:
    def __init__(self, dep_c: "DepC"):
        self.dep = dep_c


class DepC:
    pass
