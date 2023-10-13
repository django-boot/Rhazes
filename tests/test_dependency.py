from django.test import TestCase

from rhazes.dependency import DependencyProcessor
from rhazes.exceptions import DependencyCycleException, MissingDependencyException
from rhazes.scanner import class_scanner
from tests.data.di.di_cycle import (
    DepA as CycleDepA,
    DepB as CycleDepB,
    DepC as CycleDepC,
)
from tests.data.di.di_sane import DepA as SaneDepA, DepB as SaneDepB, DepC as SaneDepC


class DependencyTestCase(TestCase):
    def setUp(self) -> None:
        self.cycle_classes = class_scanner("tests.data.di.di_cycle")
        self.assertIn(CycleDepA, self.cycle_classes)
        self.assertIn(CycleDepB, self.cycle_classes)
        self.assertIn(CycleDepC, self.cycle_classes)

        self.sane_classes = class_scanner("tests.data.di.di_sane")
        self.assertIn(SaneDepA, self.sane_classes)
        self.assertIn(SaneDepB, self.sane_classes)
        self.assertIn(SaneDepC, self.sane_classes)

    def test_cycle(self):
        with self.assertRaises(DependencyCycleException) as assertion:
            DependencyProcessor(self.cycle_classes).process()
            self.assertTrue(
                all(
                    item
                    for item in self.cycle_classes
                    if item in assertion.exception.stack
                )
            )

    def test_dependency_process(self):
        objects = DependencyProcessor(self.sane_classes).process()
        self.assertIn(SaneDepA, objects)
        self.assertIn(SaneDepB, objects)
        self.assertIn(SaneDepB, objects)

    def test_dependency_process_missing_class(self):
        self.sane_classes.remove(SaneDepC)

        with self.assertRaises(MissingDependencyException) as assertion_exception:
            DependencyProcessor(self.sane_classes).process()
            self.assertEqual(assertion_exception.exception.cls, SaneDepB)
            self.assertEqual(assertion_exception.exception.missing, SaneDepC)
