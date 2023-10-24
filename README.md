# Rhazes


[![PyPI - Version](https://img.shields.io/pypi/v/django-boot-rhazes?style=flat-square)](https://pypi.org/project/django-boot-rhazes)
[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/django-boot/Rhazes/project-code-standards.yml?style=flat-square)](https://github.com/django-boot/Rhazes/actions/workflows/project-code-standards.yml)
[![GitHub issues](https://img.shields.io/github/issues/django-boot/Rhazes?style=flat-square)](https://github.com/django-boot/Rhazes/issues)
![Static Badge](https://img.shields.io/badge/Status-Under%20Development-yellow?style=flat-square&cacheSeconds=120)


A _Dependency Injection and IoC container_ library for Django Framework.


## Versions and Requirements

Written for Django 4.2 using python 3.9. _Other python versions (3.6+) should also be supported. It may work with other Django versions as well (but requires changes being applied to `setup.cfg`)._



## How it works

Once Rhazes `ApplicationContext` is initialized it will scan for classes marked with `@bean` decorator under packages listed in `settings.INSTALLED_APPS` or `settings.RHAZES_PACKAGES` (preferably).

Afterwards, it creates a graph of these classes and their dependencies to each other and starts to create objects for each class and register them as beans under `ApplicationContext`.

If everything works perfectly, you can access the beans using `ApplicationContext.get_bean(CLASS)` to get beans of a type.


## Example

Let's assume we have bean classes like below:

```python
from abc import ABC, abstractmethod
from rhazes.decorator import bean


class UserStorage(ABC):

  @abstractmethod
  def get_user(user_id: int):
    pass


@bean(_for=UserStorage, primary=False)  # primary is False by default too
class DatabaseUserStorage(UserStorage):

  def get_user(user_id: int):
    return None


@bean(_for=UserStorage, primary=True)  # set as primary implementation of UserStorage
class CacheUserStorage(UserStorage):

  def get_user(user_id: int):
    return None


@bean()
class ProductManager:

  def __init__(self, user_storage: UserStorage):
    self.user_storage = user_storage

  def get_user_products(user_id):
    user = self.user_storage.get_user(user_id)
    # Do something to find products of user?

```

Now assuming you have the above classes defined user some packages that will be scanned by Rhazes, you can access them like this:

```python
from rhazes.context import ApplicationContext
from somepackage import UserStorage, DatabaseUserStorage, CacheUserStorage,  ProductManager


application_context = ApplicationContext
# scan packages at settings.INSTALLED_APPS or settings.RHAZES_PACKAGES
application_context.initialize()

# Get ProductManager bean using its class
product_manager: ProductManager = application_context.get_bean(ProductManager)

# Get UserStorage (interface) bean
# this will be CacheUserStorage implementation since primary was set to true
user_storage: UserStorage = application_context.get_bean(UserStorage)

# Specifically get beans of classes (not the interface)
cache_user_storage: CacheUserStorage = application_context.get_bean(CacheUserStorage)  # to directly get CacheUserStorage
database_user_storage: DatabaseUserStorage = application_context.get_bean(DatabaseUserStorage)  # to directly get DatabaseUserStorage
```


### Bean factory

Bean factories are just classes that _produce_ a bean. They are beans themselves!

```python
from rhazes.protocol import BeanFactory

@bean
class SomeBeanFactory(BeanFactory):

    # optional: if you haven't defined "_for" in @bean, you can determine it here
    @classmethod
    def produces(cls):
        return SomeBean

    def produce(self):
        return SomeBean()

```


### Singleton

You can define beans as singleton.

```python
@bean(singleton=True)
class SomeBean:
    pass
```

At this point this bean will always be the same instance when being injected into another class (another bean or `@inject` (read further))


### Lazy Bean Dependencies

If the bean you are defining is depended on another bean but you don't want to immediately instantiate that other bean you can mark it as lazy.

```python

@bean
class DependencyA:
    pass


@bean(lazy_dependencies=[DependencyA])
class DependencyB:
    def __int__(self, dependency_a: DependencyA):
        self.dependency_a = dependency_a
```

Now `dependency_a` will not be instantiated (built) until there is a call to it from inside `DependencyB` instances.


### Injection

You can inject beans into _functions_ or _classes_ as long as your function (or class `__init__` function) has good support for `**kwargs`.

These classes or functions need to be called with determined input parameter names. Example:

```python

@bean
class SomeBean:
    pass


@inject()
def function(bean: SomeBean, random_input: str):
    ...

# You can call it like this:
function(random_input="something")  # `bean` will be injected automatically
```

Example for classes:

```python
@bean
class SomeBean:
    pass


@inject
class MyClazz:
    def __init__(self, bean: SomeBean, random_input: str):
        ...

MyClazz(random_input="something")  # `bean` will be injected automatically
```

To explicitly inject some beans and not others:

```python
@bean
class SomeBean1:
    pass


@bean
class SomeBean2:
    pass


@inject(injections=[SomeBean1])
def function(bean1: SomeBean1, bean2: SomeBean2, random_input: str):
    ...

# You can call it like this:
function(bean2=SomeBean2(), random_input="something")  # `bean1` will be injected automatically
```


### Inject into Django views

At this stage only injection into class views are tested. Example:

```python
@inject()
class NameGeneratorView(APIView):
    # You could optionally use @inject() here or at .setup()
    def __init__(self, string_generator: StringGeneratorService, **kwargs):
        self.string_generator = string_generator
        super(NameGeneratorView, self).__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        qs: dict = request.GET.dict()
        return Response(data={
            "name": self.string_generator.generate(
                int(qs.get("length", 10))
            )
        })
```

This example is taken [from here](https://github.com/django-boot/Rhazes-Test/blob/main/app1/views.py).

## Contribution

Read the [contribution guidelines](https://github.com/django-boot/Rhazes/blob/main/CONTRIBUTING.md).
