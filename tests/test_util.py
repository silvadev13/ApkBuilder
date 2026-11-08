import os
import sys
import unittest
from utils.util import cmd_is_available, get_bin

class TestUtil(unittest.TestCase):
    def test_cmd_is_available_true_for_existing_bin(self):
        self.assertTrue(cmd_is_available("python3"))

    def test_cmd_is_available_false_for_nonexistent_bin(self):
        self.assertFalse(cmd_is_available("nonexistent_binary_xyz_12345"))

    def test_cmd_is_available_explicit_path(self):
        python_executable = sys.executable
        self.assertTrue(cmd_is_available(python_executable))
        self.assertFalse(cmd_is_available("/tmp/non_existent_binary_path_xyz"))

    def test_get_bin(self):
        path = get_bin("python3")
        self.assertIsNotNone(path)
        self.assertTrue(path.endswith("python3"))

    def test_caching_behavior(self):
        get_bin.cache_clear()
        cmd_is_available.cache_clear()

        # Initial call creates a cache miss
        self.assertTrue(cmd_is_available("python3"))
        info1 = cmd_is_available.cache_info()
        self.assertEqual(info1.misses, 1)
        self.assertEqual(info1.hits, 0)

        # Subsequent call uses cache (hits increment)
        self.assertTrue(cmd_is_available("python3"))
        info2 = cmd_is_available.cache_info()
        self.assertEqual(info2.hits, 1)

        # get_bin cache inspection
        get_bin.cache_clear()
        get_bin("python3")
        self.assertEqual(get_bin.cache_info().misses, 1)
        get_bin("python3")
        self.assertEqual(get_bin.cache_info().hits, 1)

if __name__ == "__main__":
    unittest.main()
