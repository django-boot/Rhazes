from django.test import TestCase

from rhazes.dependency import DependencyProcessor
from rhazes.exceptions import DependencyCycleException
from rhazes.scanner import ModuleScanner, class_scanner
from tests.data.di.di_cycle import DepA, DepB, DepC


class DependencyTestCase(TestCase):

    def setUp(self) -> None:
        self.classes = class_scanner("tests.data.di.di_cycle")
        self.assertIn(DepA, self.classes)
        self.assertIn(DepB, self.classes)
        self.assertIn(DepC, self.classes)

    def test_cycle(self):
        with self.assertRaises(DependencyCycleException) as assertion:
            DependencyProcessor(self.classes).process()
            self.assertTrue(all([item for item in self.classes if item in assertion.exception.stack]))
