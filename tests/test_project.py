import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from core.project import Project

class TestProjectCaching(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = self.temp_dir.name

        # Create minimal project structure
        with open(os.path.join(self.project_dir, "project.yml"), "w") as f:
            f.write("""
bins:
    aapt2: /usr/bin/stub
    javac: /usr/bin/stub
    kotlinc: /usr/bin/stub
    d8: /usr/bin/stub
    apksigner: /usr/bin/stub

android:
    sdk-api-version: 34
    sdk-min-api-version: 21
    version-code: 1
    version-name: "1"
    build-type: debug
    keystore-path: test.keystore
    keystore-alias: test
    keystore-store-pass: pass
    keystore-key-pass: pass
""")

        os.makedirs(os.path.join(self.project_dir, "src", "java"), exist_ok=True)

        manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.test">
</manifest>
"""
        with open(os.path.join(self.project_dir, "AndroidManifest.xml"), "w") as f:
            f.write(manifest_content)

        # Create keystore stub
        with open(os.path.join(self.project_dir, "test.keystore"), "w") as f:
            f.write("dummy keystore")

        # Create libs directory with dummy jar and manifest
        self.libs_dir = os.path.join(self.project_dir, ".libs")
        lib1_dir = os.path.join(self.libs_dir, "lib1")
        os.makedirs(lib1_dir, exist_ok=True)
        with open(os.path.join(lib1_dir, "classes.jar"), "w") as f:
            f.write("dummy jar")
        with open(os.path.join(lib1_dir, "AndroidManifest.xml"), "w") as f:
            f.write("""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.lib1">
</manifest>""")

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("utils.util.get_bin", return_value="/usr/bin/stub")
    @patch("os.getenv", return_value="/tmp/android-sdk")
    def test_find_lib_jars_caching(self, mock_getenv, mock_get_bin):
        proj = Project(self.project_dir)

        # First call populates cache
        jars1 = proj.find_lib_jars()
        self.assertEqual(len(jars1), 1)
        self.assertTrue(jars1[0].endswith("classes.jar"))
        self.assertIsNotNone(proj._cached_lib_jars)

        # Add another jar to filesystem after first call
        lib2_dir = os.path.join(self.libs_dir, "lib2")
        os.makedirs(lib2_dir, exist_ok=True)
        with open(os.path.join(lib2_dir, "classes2.jar"), "w") as f:
            f.write("dummy jar 2")

        # Second call returns cached result without re-scanning disk
        jars2 = proj.find_lib_jars()
        self.assertEqual(len(jars2), 1)
        self.assertEqual(jars1, jars2)

    @patch("utils.util.get_bin", return_value="/usr/bin/stub")
    @patch("os.getenv", return_value="/tmp/android-sdk")
    def test_get_lib_package_names_caching(self, mock_getenv, mock_get_bin):
        proj = Project(self.project_dir)

        pkg_names1 = proj.get_lib_package_names()
        self.assertEqual(pkg_names1, "com.example.lib1")
        self.assertEqual(proj._cached_lib_package_names, "com.example.lib1")

        # Call again to verify cached return
        pkg_names2 = proj.get_lib_package_names()
        self.assertEqual(pkg_names2, "com.example.lib1")

    @patch("utils.util.get_bin", return_value="/usr/bin/stub")
    @patch("os.getenv", return_value="/tmp/android-sdk")
    def test_find_files_nonexistent_dir(self, mock_getenv, mock_get_bin):
        proj = Project(self.project_dir)

        nonexistent = os.path.join(self.project_dir, "does_not_exist")
        result = proj.find_files(nonexistent, ".java")
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()
