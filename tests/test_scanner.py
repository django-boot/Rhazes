from django.test import TestCase

from rhazes.scanner import ModuleScanner


class ModuleScannerTestCase(TestCase):
    def test_scanner(self):
        scanner = ModuleScanner(["tests.data.scanner"])
        results = scanner.scan()
        self.assertIn("tests.data.scanner.package", results)
        self.assertIn("tests.data.scanner.package.module", results)
