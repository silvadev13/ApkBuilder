from utils.util import run, get_logger, cmd_is_available
from core.project import Project
import zipfile
import shutil
import os

class Task:
    def __init__(self, project: Project):
        self.project = project
        self.android_jar = os.path.join(self.project.sdk_dir, "platforms", f"android-{self.project.target_sdk}", "android.jar")
    
    def prepare(self):
        pass
    
    def __sign_apk(self):
        get_logger().info("-- Signing Apk")
    
        apksigner_available = cmd_is_available(self.project.bin_apksigner)
        if not apksigner_available:
            raise Exception("> apksigner not detected in PATH or SDK build-tools. Please set it in PATH.")
    
        run([
            self.project.bin_apksigner, "sign",
            "--ks", self.project.keystore_file,
            "--ks-key-alias", self.project.keystore_alias,
            "--ks-pass", f"pass:{self.project.keystore_store_pass}",
            "--key-pass", f"pass:{self.project.keystore_key_pass}",
            "--out", os.path.join(self.project.bin_dir, "gen.apk"),
            "--in", os.path.join(self.project.bin_dir, "unsigned.apk")
        ])
        
        os.remove(os.path.join(self.project.bin_dir, "unsigned.apk"))

    def start(self):
        get_logger().info("-- Packaging Apk")
        
        out_apk = os.path.join(self.project.bin_dir, "unsigned.apk")
        shutil.copy2(os.path.join(self.project.bin_dir, "gen.apk.res"), out_apk)
    
        with zipfile.ZipFile(out_apk, "a", zipfile.ZIP_DEFLATED) as apk:

            dex_files = self.project.find_dex_files()
            if not dex_files:
                raise ValueError("-- no dex files found")

            for dex in dex_files:
                name = os.path.basename(dex)
                apk.write(dex, name)
            
            dex_index = len(dex_files) + 1
            for library in self.project.find_lib_jars():
                library_dir = os.path.dirname(library)
                library_dex_files = self.project.find_files(library_dir, ".dex")
                if not library_dex_files:
                    continue
                
                for dex in library_dex_files:
                    name = f"classes{dex_index}.dex"
                    apk.write(dex, name)
                    dex_index += 1

            native_libs = self.project.find_native_libs()
            for abi, so in native_libs:
                arc = f"lib/{abi}/{os.path.basename(so)}"
                apk.write(so, arc)
        
        self.__sign_apk()
