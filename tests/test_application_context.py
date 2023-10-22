from django.test import TestCase, override_settings

from rhazes.context import ApplicationContext
from tests.data.di.context.di_context import SomeABC, DepAI1, DepB, DepC
from tests.data.di.factory.di_factory import SomeInterface, TestStringGeneratorBean


@override_settings(RHAZES_PACKAGES=["tests.data.di.context", "tests.data.di.factory"])
class ApplicationContextTestCase(TestCase):
    def setUp(self) -> None:
        self.application_context = ApplicationContext()
        self.application_context.initialize()

    def test_bean_context(self):
        """
        Assures in happy scenarios bean classes are registered and are accessible in application context
        """
        self.assertTrue(self.application_context._initialized)
        self.assertTrue(
            isinstance(self.application_context.beans.get_bean(SomeABC), DepAI1)
        )
        self.assertIsNotNone(self.application_context.beans.get_bean(DepAI1))
        self.assertIsNotNone(self.application_context.beans.get_bean(DepB))
        self.assertIsNotNone(self.application_context.beans.get_bean(DepC))
        dep_b: DepB = self.application_context.beans.get_bean(DepB)
        self.assertEqual(dep_b.dep, self.application_context.beans.get_bean(DepC))

    def test_factory_context(self):
        """
        Assures in happy scenarios bean factories produce beans and are registered in application context
        """
        self.assertTrue(self.application_context._initialized)
        self.assertIsNotNone(self.application_context.beans.get_bean(SomeInterface))
        self.assertTrue(
            isinstance(
                self.application_context.beans.get_bean(SomeInterface), SomeInterface
            )
        )
        test_string_generator: TestStringGeneratorBean = (
            self.application_context.beans.get_bean(TestStringGeneratorBean)
        )
        self.assertIsNotNone(test_string_generator)
        si: SomeInterface = self.application_context.beans.get_bean(SomeInterface)
        self.assertEqual(si.name(), test_string_generator.get_string())
