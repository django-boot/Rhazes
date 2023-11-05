from rhazes.bean_builder import (
    DefaultBeanBuilderStrategy,
    SingletonBeanBuilderStrategy,
)


class Scope:
    DEFAULT = DefaultBeanBuilderStrategy
    SINGLETON = SingletonBeanBuilderStrategy
