# Rhazes

![Static Badge](https://img.shields.io/badge/Status-Under%20Development-yellow?style=flat-square&cacheSeconds=120)


A _Dependency Injection_ framework for Django Framework.


## Versions and Requirements

_There is no published version yet_. Written for Django 4.2 using python 3.9. Other python versions (3.6+) should be supported. It may work with other Django versions as well (after required changes being applied to `setup.cfg`.

## How it works

Once Rhazes `ApplicationContext` is initialized it will scan for classes marked with `@service` decorator under packages listed in `settings.INSTALLED_APPS` or `settings.RHAZES_PACKAGES` (preferably).

Afterwards, it creates a graph of these classes and their dependencies to each other and starts to create objects for each class and register them as beans under `ApplicationContext().beans`.

If everything works perfectly, you can access the beans using `ApplicationContext().beans.get_bean(CLASS)` for a class.


## Example

Lets assume we have service classes like below: 

```python
from abc import ABC, abstractmethod
from rhazes.decorator import service


class UserStorage(ABC):

  @abstractmethod
  def get_user(user_id: int):
    pass


@service(_for=UserStorage, primary=False)  # primary is False by default too
class DatabaseUserStorage(UserStorage):

  def get_user(user_id: int):
    return None 


@service(_for=UserStorage, primary=True)  # set as primary implementation of UserStorage
class CacheUserStorage(UserStorage):

  def get_user(user_id: int):
    return None 


@service()
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


application_context = ApplicationContext()
application_context.initialize()

product_manager: ProductManager = application_context.beans.get_bean(ProductManager)
user_storage: UserStorage = application_context.beans.get_bean(UserStorage)  # this will be CacheUserStorage implementation since primary was set to true

cache_user_storage: CacheUserStorage = application_context.beans.get_bean(CacheUserStorage)  # to directly get CacheUserStorage
database_user_storage: DatabaseUserStorage = application_context.beans.get_bean(DatabaseUserStorage)  # to directly get DatabaseUserStorage

```


## Contribution

Read the [contribution guidelines](https://github.com/django-boot/Rhazes/blob/main/CONTRIBUTING.md).

