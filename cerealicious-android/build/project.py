from utils.util import get_logger, get_bin
import xml.etree.ElementTree as ET
import os
import yaml


class Project:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.yml_file = os.path.join(self.project_dir, "project.yml")

        if not os.path.exists(self.yml_file):
            raise Exception("-- project.yml does not exist")

        with open(self.yml_file, "r") as f:
            self.config = yaml.safe_load(f) or {}
            if not self.config:
                raise Exception("-- project.yml is empty")
            if "android" not in self.config:
                raise Exception("-- missing 'android' section in project.yml")
            self.config_android = self.config["android"]

        self.min_sdk      = self.config_android.get("sdk-min-api-version", 21)
        self.target_sdk   = self.config_android.get("sdk-api-version", 31)
        self.version_code = self.config_android.get("version-code", 1)
        self.version_name = self.config_android.get("version-name", "1")

        self.build_type = self.config_android.get("build-type", "debug")
        if self.build_type not in ("release", "debug"):
            raise Exception("-- build type invalid (must be 'debug' or 'release')")

        self.enable_view_binding = self.config_android.get("view-binding", False)

        # ── Keystore (bugfix: check the raw value before joining) ──
        keystore_rel = self.config_android.get("keystore-path")
        if not keystore_rel:
            raise Exception("-- keystore-path not declared in project.yml")
        self.keystore_file = os.path.join(self.project_dir, keystore_rel)

        self.keystore_alias      = self.config_android["keystore-alias"]
        self.keystore_store_pass = self.config_android["keystore-store-pass"]
        self.keystore_key_pass   = self.config_android["keystore-key-pass"]

        self.java_version = self.config_android.get("java-version", 17)

        # ── Source directories ──
        self.assets_dir     = os.path.join(self.project_dir, self.config_android.get("assets-path", "src/assets"))
        self.native_libs_dir= os.path.join(self.project_dir, self.config_android.get("jni-path", "src/jniLibs"))
        self.res_dir        = os.path.join(self.project_dir, self.config_android.get("res-path", "src/res"))

        self.sources_dir = os.path.join(self.project_dir, self.config_android.get("sources-path", "src/java"))
        if not os.path.exists(self.sources_dir):
            raise Exception(f"-- sources dir does not exist: {self.sources_dir}")

        self.manifest_file = os.path.join(self.project_dir, self.config_android.get("manifest-path", "AndroidManifest.xml"))
        if not os.path.exists(self.manifest_file):
            raise Exception(f"-- AndroidManifest.xml does not exist: {self.manifest_file}")

        self.package_name = ET.parse(self.manifest_file).getroot().attrib.get("package")
        if not self.package_name:
            raise Exception("-- AndroidManifest.xml needs the 'package' attr")

        # ── Output directories ──
        self.libs_dir    = os.path.join(self.project_dir, self.config.get("libs-path", ".libs"))
        self.output_dir  = os.path.join(self.project_dir, self.config.get("build-path", ".build"))
        self.gen_dir     = os.path.join(self.output_dir, "gen")
        self.bin_dir     = os.path.join(self.output_dir, "bin")

        self.java_classes_dir   = os.path.join(self.bin_dir, "java", "classes")
        self.kotlin_classes_dir = os.path.join(self.bin_dir, "kotlin", "classes")
        self.compiled_res_dir   = os.path.join(self.bin_dir, "res")
        self.dex_dir            = os.path.join(self.bin_dir, "dex")
        self.view_binding_dir   = os.path.join(self.output_dir, "view_binding")

        # ── Binaries ──
        self.__config_bin = self.config.get("bins", {})
        self.bin_aapt2     = self.__resolve_bin("aapt2")
        self.bin_javac     = self.__resolve_bin("javac")
        self.bin_kotlinc   = self.__resolve_bin("kotlinc")
        self.bin_d8        = self.__resolve_bin("d8")
        self.bin_apksigner = self.__resolve_bin("apksigner")

        self.sdk_dir = self.__resolve_sdk_path()

    # ── Private helpers ──────────────────────────────────────────────────────

    def __resolve_sdk_path(self):
        sdk_path = self.config_android.get("sdk-path")
        if sdk_path:
            return sdk_path
        sdk_path = os.getenv("ANDROID_SDK") or os.getenv("ANDROID_HOME")
        if not sdk_path:
            raise Exception("Neither env(ANDROID_SDK) nor env(ANDROID_HOME) are defined.")
        get_logger().info(f"-- no android:sdk-path provided. falling back to {sdk_path}")
        return sdk_path

    def __resolve_bin(self, name):
        path = self.__config_bin.get(name)
        if path:
            return path
        fallback = get_bin(name)
        if fallback:
            get_logger().info(f"-- no bins:{name} provided. falling back to {fallback}")
            return fallback
        raise Exception(f"-- bin '{name}' not found and no fallback available")

    # ── Public helpers ───────────────────────────────────────────────────────

    def get_lib_package_names(self):
        packages = set()
        for root, _, files in os.walk(self.libs_dir):
            for f in files:
                if f != "AndroidManifest.xml":
                    continue
                pkg = ET.parse(os.path.join(root, f)).getroot().attrib.get("package")
                if pkg:
                    packages.add(pkg)
        return ":".join(sorted(packages))

    def find_files(self, base_dir, suffix):
        result = []
        if not base_dir:
            get_logger().error("-- no base dir found")
            return result
        if not os.path.isdir(base_dir):
            get_logger().error(f"-- base dir is not a directory: {base_dir}")
            return result
        for root, _, files in os.walk(base_dir):
            for f in files:
                if f.endswith(suffix):
                    result.append(os.path.join(root, f))
        return result

    def find_java_files(self, base_dir=None):
        return self.find_files(base_dir or self.sources_dir, ".java")

    def find_kotlin_files(self, base_dir=None):
        return self.find_files(base_dir or self.sources_dir, ".kt")

    def find_lib_jars(self):
        jars = []
        for root, _, files in os.walk(self.libs_dir):
            for f in files:
                if f.endswith(".jar") and f != "lint.jar":
                    jars.append(os.path.join(root, f))
        return jars

    def find_dex_files(self):
        if not os.path.isdir(self.dex_dir):
            return []
        return [
            os.path.join(self.dex_dir, f)
            for f in os.listdir(self.dex_dir)
            if f.endswith(".dex")
        ]

    def find_native_libs(self):
        libs = []
        if not self.native_libs_dir or not os.path.isdir(self.native_libs_dir):
            return libs
        for abi in os.listdir(self.native_libs_dir):
            abi_dir = os.path.join(self.native_libs_dir, abi)
            if not os.path.isdir(abi_dir):
                continue
            for f in os.listdir(abi_dir):
                if f.endswith(".so"):
                    libs.append((abi, os.path.join(abi_dir, f)))
        return libs

    def android_jar(self):
        """Path to android.jar for the target SDK."""
        return os.path.join(
            self.sdk_dir,
            "platforms",
            f"android-{self.target_sdk}",
            "android.jar",
        )

    def build_tools_dir(self):
        """Path to the latest installed build-tools."""
        bt_root = os.path.join(self.sdk_dir, "build-tools")
        if not os.path.isdir(bt_root):
            raise Exception(f"-- build-tools not found at {bt_root}")
        versions = sorted(os.listdir(bt_root), reverse=True)
        if not versions:
            raise Exception("-- no build-tools versions installed")
        return os.path.join(bt_root, versions[0])
