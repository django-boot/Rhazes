class MissingDependencyException(Exception):
    def __init__(self, cls, missing):
        self.cls = cls
        self.missing = missing
        super().__init__(
            f"Class {cls} depends on {missing} which was not found during scan!"
        )


class DependencyCycleException(Exception):
    def __init__(self, stack, breaker):
        cycle = " -> ".join([str(item) for item in stack])
        cycle += f" -> {str(breaker)}"
        self.stack = stack
        self.breaker = breaker
        super().__init__(f"Dependency Cycle Detected!\n{cycle}")
