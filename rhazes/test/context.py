from rhazes.context import ApplicationContext


class TemporaryContext:

    def __init__(self):
        self.old_values = {}

    def register_bean(self, clazz, obj):
        old_value = ApplicationContext.get_bean(clazz)
        if clazz not in self.old_values:
            self.old_values[clazz] = old_value
        ApplicationContext.register_bean(clazz, lambda x: obj, True)

    def reset(self):
        for clazz, old_value in self.old_values.items():
            ApplicationContext.register_bean(clazz, lambda x: old_value, True)


class TemporaryContextManager:

    def __init__(self):
        self.temporary_context = TemporaryContext()

    def __enter__(self):
        return self.temporary_context

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.temporary_context.reset()
