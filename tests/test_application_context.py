from django.test import TestCase, override_settings

from rhazes.context import ApplicationContext
from tests.data.di.di_context import SomeABC, DepAI1, DepAI2, DepB, DepC


@override_settings(RHAZES_PACKAGES=["tests.data.di"])
class DependencyTestCase(TestCase):

    def setUp(self) -> None:
        self.application_context = ApplicationContext()

    def test_context(self):
        self.application_context.initialize()
        self.assertTrue(self.application_context._initialized)
        self.assertTrue(
            isinstance(self.application_context.beans.get_bean(SomeABC), DepAI1)
        )
        self.assertIsNotNone(self.application_context.beans.get_bean(DepAI1))
        self.assertIsNotNone(self.application_context.beans.get_bean(DepB))
        self.assertIsNotNone(self.application_context.beans.get_bean(DepC))
