import functools
import inspect
from typing import Optional, Dict, Type, List, Union

from rhazes.context import ApplicationContext
from rhazes.protocol import InjectionConfiguration, BeanDetails


def bean(
    _for=None,
    primary=False,
    singleton=False,
    lazy_dependencies: Optional[List[Union[type, str]]] = None,
):
    def decorator(cls):
        if _for is not None and not issubclass(cls, _for):
            raise Exception(
                f"{cls} bean is meant to be registered for interface {_for} "
                f"but its not a subclass of that interface"
            )

        @functools.wraps(cls, updated=())
        class DecoratedBean(cls):
            @classmethod
            def bean_details(cls) -> BeanDetails:
                return BeanDetails(_for, primary, singleton, lazy_dependencies)

        return DecoratedBean

    return decorator


def inject_kwargs(injections, configuration, func, kwargs: dict):
    signature = inspect.signature(func)
    for k, v in signature.parameters.items():
        if k in ["self", "cls"]:
            continue

        if k in ["args", "kwargs"]:
            continue

        if (injections is not None and v.annotation in injections) or (
            injections is None and v.annotation is not None
        ):
            lazy = configuration.get(v.annotation, {}).get("lazy", False)
            if lazy:
                dep = ApplicationContext.get_lazy_bean(v.annotation)
            else:
                dep = ApplicationContext.get_bean(v.annotation)
            if dep is not None:
                kwargs[k] = dep
        return kwargs


def inject(injections=None, configuration: Dict[Type, InjectionConfiguration] = None):
    if configuration is None:
        configuration = {}

    def decorator(obj_of_func):

        if isinstance(obj_of_func, type):
            # We are dealing with a class
            @functools.wraps(obj_of_func, updated=())
            class Proxy(obj_of_func):
                def __init__(self, *args, **kwargs):
                    inject_kwargs(
                        injections, configuration, obj_of_func.__init__, kwargs
                    )
                    super(obj_of_func, self).__init__(*args, **kwargs)

            return Proxy

        elif callable(obj_of_func):

            if obj_of_func.__name__ == "__init__":  # constructor

                def proxy(obj, *args, **kwargs):
                    inject_kwargs(injections, configuration, obj_of_func, kwargs)
                    return obj_of_func(obj, *args, **kwargs)

                return proxy
            else:

                def proxy(*args, **kwargs):
                    inject_kwargs(injections, configuration, obj_of_func, kwargs)
                    return obj_of_func(*args, **kwargs)

                return proxy

        else:
            return obj_of_func

    return decorator
