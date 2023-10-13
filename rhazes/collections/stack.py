from collections import deque


class UniqueStack(deque):

    def _validate_unique(self, value):
        for i in self:
            if value == i:
                raise Exception("Item already in stack")  # Todo

    def append(self, *args, **kwargs):
        self._validate_unique(args[0])
        return super(UniqueStack, self).append(*args, **kwargs)

    def appendleft(self, *args, **kwargs) -> None:
        self._validate_unique(args[0])
        return super(UniqueStack, self).appendleft(*args, **kwargs)