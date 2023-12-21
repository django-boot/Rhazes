from unittest import TestCase

from rhazes.context import ApplicationContext
from rhazes.test.context import TemporaryContext, TemporaryContextManager
from rhazes.utils import LazyObject

from tests.data.di.context.di_context import (
    SomeABC,
    DepAI1,
    DepAI2,
    DepB,
    DepC,
    DepD,
    DepE,
)
from tests.data.di.factory.di_factory import (
    SomeInterface,
    TestStringGeneratorBean,
    SomeInterfaceUsage,
)


class ApplicationContextTestCase(TestCase):
    def setUp(self) -> None:
        self.application_context = ApplicationContext
        self.application_context.initialize(
            ["tests.data.di.context", "tests.data.di.factory"]
        )

    def test_bean_context(self):
        """
        Assures in happy scenarios bean classes are registered and are accessible in application context
        """
        self.assertTrue(self.application_context._initialized)
        self.assertTrue(isinstance(self.application_context.get_bean(SomeABC), DepAI1))
        self.assertIsNotNone(self.application_context.get_bean(DepAI1))
        self.assertIsNotNone(self.application_context.get_bean(DepB))
        self.assertIsNotNone(self.application_context.get_bean(DepC))

    def test_singleton_beans(self):
        # Singleton DepC is used in DepB
        dep_b: DepB = self.application_context.get_bean(DepB)
        self.assertEqual(dep_b.dep_c, self.application_context.get_bean(DepC))
        # Not a singleton DepD is used in DepB
        self.assertNotEqual(dep_b.dep_d, self.application_context.get_bean(DepD))

    def test_lazy_dependencies(self):
        dep_e: DepE = self.application_context.get_bean(DepE)
        dep_d: DepD = self.application_context.get_bean(DepD)
        self.assertTrue(isinstance(dep_e.dep_d, LazyObject))
        self.assertTrue(isinstance(dep_e, DepE))
        self.assertEqual(dep_e.dep_d.name(), dep_d.name())

    def test_factory_context(self):
        """
        Assures in happy scenarios bean factories produce beans and are registered in application context
        """
        self.assertTrue(self.application_context._initialized)
        self.assertIsNotNone(self.application_context.get_bean(SomeInterface))
        self.assertTrue(
            isinstance(self.application_context.get_bean(SomeInterface), SomeInterface)
        )
        test_string_generator: TestStringGeneratorBean = (
            self.application_context.get_bean(TestStringGeneratorBean)
        )
        self.assertIsNotNone(test_string_generator)
        si: SomeInterface = self.application_context.get_bean(SomeInterface)
        self.assertEqual(si.name(), test_string_generator.get_string())

    def test_factory_product_as_dependency(self):
        self.assertTrue(self.application_context._initialized)
        self.assertIsNotNone(self.application_context.get_bean(SomeInterfaceUsage))
        usage: SomeInterfaceUsage = self.application_context.get_bean(
            SomeInterfaceUsage
        )
        self.assertIsNotNone(usage.get_name())
        # print(usage.get_name())


class TemporaryContextTestCase(TestCase):
    def setUp(self) -> None:
        self.application_context = ApplicationContext
        self.application_context.initialize(
            ["tests.data.di.context", "tests.data.di.factory"]
        )

    def test_temporary_context(self):
        self.assertTrue(isinstance(self.application_context.get_bean(SomeABC), DepAI1))
        temporary_context = TemporaryContext()
        temporary_context.register_bean(
            SomeABC, DepAI2(self.application_context.get_bean(DepB))
        )
        self.assertTrue(isinstance(self.application_context.get_bean(SomeABC), DepAI2))
        temporary_context.reset()
        self.assertTrue(isinstance(self.application_context.get_bean(SomeABC), DepAI1))

    def test_temporary_context_manager(self):
        self.assertTrue(isinstance(self.application_context.get_bean(SomeABC), DepAI1))

        with TemporaryContextManager() as manager:
            manager.register_bean(
                SomeABC, DepAI2(self.application_context.get_bean(DepB))
            )
            self.assertTrue(
                isinstance(self.application_context.get_bean(SomeABC), DepAI2)
            )

        self.assertTrue(isinstance(self.application_context.get_bean(SomeABC), DepAI1))
