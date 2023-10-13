from collections import deque


class UniqueStack(deque):
    def _validate_unique(self, value):
        for i in self:
            if value == i:
                raise ValueError("Item already in stack")

    def append(self, *args, **kwargs):
        self._validate_unique(args[0])
        return super(UniqueStack, self).append(*args, **kwargs)

    def appendleft(self, *args, **kwargs) -> None:
        self._validate_unique(args[0])
        return super(UniqueStack, self).appendleft(*args, **kwargs)
