from logging import getLevelNamesMapping
from .core import run, get_logger, cmd_is_available
from .project import Project
import zipfile
import shutil
import os

class APK:
    def __init__(self, project: Project):
        self.tools = os.path.abspath("./build_logic/tools")
        self.aapt2 = os.path.join(self.tools, "aapt2")
        self.android_jar = os.path.join(self.tools, "android.jar")
        self.project = project
    
    def prepare(self):
        pass
    
    def __sign_apk(self):
        get_logger().info("> signingApk")
        
        testkey = os.path.join(self.tools, "testkey.pk8")
        if not testkey:
            get_logger().error("Testkey not found")
            return
        testcert = os.path.join(self.tools, "testkey.x509.pem")
        if not testcert:
            get_logger().error("Testcert not found")
            return
    
        apksigner_available = cmd_is_available("apksigner")
        if not apksigner_available:
            get_logger().error("> apksigner not detected in PATH. Please set it in PATH.")
            return
    
        run([
            "apksigner", "sign",
            "--key", testkey,
            "--cert", testcert,
            "--min-sdk-version", str(self.project.get_min_sdk()),
            "--max-sdk-version", str(self.project.get_target_sdk()),
            "--out", os.path.join(self.project.get_bin_dir(), "gen.apk"),
            "--in", os.path.join(self.project.get_bin_dir(), "unsigned.apk")
        ])
        
        os.remove(os.path.join(self.project.get_bin_dir(), "unsigned.apk"))

    def start(self):
        get_logger().info("> packagingApk")
        
        out_apk = os.path.join(self.project.get_bin_dir(), "unsigned.apk")
        shutil.copy2(os.path.join(self.project.get_bin_dir(), "gen.apk.res"), out_apk)
    
        with zipfile.ZipFile(out_apk, "a", zipfile.ZIP_DEFLATED) as apk:

            # add dex files
            dex_files = self.project.find_dex_files()
            if not dex_files:
                raise ValueError("No dex files found")

            for dex in dex_files:
                name = os.path.basename(dex)
                apk.write(dex, name)

            # add native libs
            native_libs = self.project.find_native_libs()
            for abi, so in native_libs:
                arc = f"lib/{abi}/{os.path.basename(so)}"
                apk.write(so, arc)
        
        self.__sign_apk()
