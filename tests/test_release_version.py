import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("release_version", Path(__file__).resolve().parents[1] / "scripts/release_version.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReleaseVersionTests(unittest.TestCase):
    def test_sequence_increases_semantic_prerelease(self):
        self.assertEqual(module.release_version("0.1.0-alpha.0", 9), "0.1.0-alpha.9")
        self.assertEqual(module.release_version("0.1.0-alpha.0", 10), "0.1.0-alpha.10")

    def test_rerun_has_same_version(self):
        self.assertEqual(module.release_version("0.1.0-alpha.0", 42), module.release_version("0.1.0-alpha.0", 42))

    def test_stable_release_is_not_automatic(self):
        for base in ("1.0.0", "0.1.0", "0.1.0-alpha.01", "01.1.0-alpha.0"):
            with self.subTest(base=base), self.assertRaises(ValueError):
                module.release_version(base, 1)

    def test_sequence_must_be_positive(self):
        for sequence in (0, -1):
            with self.subTest(sequence=sequence), self.assertRaises(ValueError):
                module.release_version("0.1.0-alpha.0", sequence)
