from django.test import TestCase, override_settings

from rhazes.context import ApplicationContext
from rhazes.decorator import inject
from tests.data.di.context.di_context import DepD, DepE


@override_settings(RHAZES_PACKAGES=["tests.data.di.context", "tests.data.di.factory"])
class InjectionTestCase(TestCase):
    def setUp(self) -> None:
        self.application_context = ApplicationContext
        self.application_context.initialize()
        self.dep_d: DepD = self.application_context.get_bean(DepD)
        self.assertIsNotNone(self.dep_d)

    def test_single_bean_injection(self):
        @inject()
        def echo(dep_d: DepD, inp: str):
            return f"{inp}+{dep_d.name()}"

        result = echo(inp="test")
        self.assertEqual(f"test+{self.dep_d.name()}", result)

    def test_unknown_bean_injection(self):
        class Unkown:
            pass

        @inject()
        def echo(unkown: Unkown, inp: str):
            return inp

        with self.assertRaises(TypeError):
            echo(inp="test")

    def test_optional_dependency(self):
        @inject(injections=[DepD])
        def echo(dep_d: DepD, dep_e: DepE, inp: str):
            return f"{inp}+{dep_e.dep_d.name()}"

        with self.assertRaises(TypeError):
            echo(inp="test")

        dep_e = self.application_context.get_bean(DepE)
        result = echo(dep_e=dep_e, inp="test")
        self.assertEqual(f"test+{self.dep_d.name()}", result)
