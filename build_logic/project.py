from .core import get_logger
import os
import xml.etree.ElementTree as ET

class Project:
    def __init__(self, project_dir, min_sdk, target_sdk, version_code, version_name, enable_view_binding):
        self.__min_sdk = min_sdk
        self.__target_sdk = target_sdk
        self.__version_code = version_code
        self.__version_name = version_name
        self.__enable_view_binding = enable_view_binding
        self.__app_dir = os.path.join(project_dir, "app")
        if not self.__app_dir:
            get_logger().error("No app module found")
            return
        
        #main paths/files
        self.__main_dir = os.path.join(self.__app_dir, "src", "main")
        self.__assets_dir = os.path.join(self.__main_dir, "assets")
        self.__native_libs_dir = os.path.join(self.__main_dir, "jniLibs")
        self.__res_dir = os.path.join(self.__main_dir, "res")
        self.__manifest_file = os.path.join(self.__main_dir, "AndroidManifest.xml")
        self.__package_name = ET.parse(self.__manifest_file).getroot().attrib.get("package")
        
        #libs path
        self.__libs_dir = os.path.join(self.__app_dir, "libs")
        
        #output path
        self.__output_dir = os.path.join(self.__app_dir, "build")       
        #this dir servers only to aapt generate files
        self.__gen_dir = os.path.join(self.__output_dir, "gen")
        #this dir servers to generate apk
        self.__bin_dir = os.path.join(self.__output_dir, "bin")
        self.__java_classes_dir = os.path.join(self.__bin_dir, "java", "classes")
        self.__kotlin_classes_dir = os.path.join(self.__bin_dir, "kotlin", "classes")
        self.__compiled_res_dir = os.path.join(self.__bin_dir, "res")
        #this dir servers to generated view binding files
        self.__view_binding_dir = os.path.join(self.__output_dir, "view_binding")
    
    def get_min_sdk(self):
        return self.__min_sdk
    
    def get_target_sdk(self):
        return self.__target_sdk
    
    def get_version_code(self):
        return self.__version_code
    
    def get_version_name(self):
        return self.__version_code
    
    def get_package_name(self):
        return self.__package_name
    
    def get_enable_view_binding(self):
        return self.__enable_view_binding
    
    def get_app_dir(self):
        return self.__app_dir
    
    def get_main_dir(self):
        return self.__main_dir
    
    def get_assets_dir(self):
        return self.__assets_dir
    
    def get_native_libs_dir(self):
        return self.__native_libs_dir
    
    def get_res_dir(self):
        return self.__res_dir
    
    def get_manifest_file(self):
        return self.__manifest_file
    
    def get_libs_dir(self):
        return self.__libs_dir
    
    def get_output_dir(self):
        return self.__output_dir
    
    def get_gen_dir(self):
        return self.__gen_dir
    
    def get_bin_dir(self):
        return self.__bin_dir
    
    def get_java_classes_dir(self):
        return self.__java_classes_dir
    
    def get_kotlin_classes_dir(self):
        return self.__kotlin_classes_dir
    
    def get_compiled_res_dir(self):
        return self.__compiled_res_dir
    
    def get_view_binding_dir(self):
        return self.__view_binding_dir
    
    def get_lib_package_names(self):
        packages = set()
        
        for root, _, files in os.walk(self.get_libs_dir()):
            for f in files:
                if f != "AndroidManifest.xml":
                    continue
                
                manifest_file = os.path.join(root, f)
                pkg = ET.parse(manifest_file).getroot().attrib.get("package")
                if pkg:
                    packages.add(pkg)
        
        return ":".join(sorted(packages))
    
    def find_files(self, base_dir, suffix):
        result = []
        
        if not base_dir:
            get_logger().error("No base dir found")
            return result
        
        if not os.path.isdir(base_dir):
            get_logger().error("Base dir cannot be file")
            return result
        
        for root, _, files in os.walk(base_dir):
            for f in files:
                if f.endswith(suffix):
                    result.append(os.path.join(root, f))
        return result
    
    def find_java_files(self, base_dir=None):
        base_dir = base_dir if base_dir else self.get_main_dir()
        return self.find_files(base_dir, ".java")
    
    def find_kotlin_files(self, base_dir=None):
        base_dir = base_dir if base_dir else self.get_main_dir()
        return self.find_files(base_dir, ".kt")
    
    def find_lib_jars(self):
        jars = []
        for root, _, files in os.walk(self.get_libs_dir()):
            for f in files:
                if f.endswith(".jar") and f != "lint.jar":
                    jars.append(os.path.join(root, f))
        return jars
    
    def find_dex_files(self):
        return [
            os.path.join(self.get_bin_dir(), f)
            for f in os.listdir(self.get_bin_dir())
            if f.endswith(".dex")
        ]
    
    def find_native_libs(self):
        libs = []
    
        if not self.get_native_libs_dir():
            return libs

        if not os.path.isdir(self.get_native_libs_dir()):
            return libs

        for abi in os.listdir(self.get_native_libs_dir()):
            abi_dir = os.path.join(self.get_native_libs_dir(), abi)
            if not os.path.isdir(abi_dir):
                continue

            for f in os.listdir(abi_dir):
                if f.endswith(".so"):
                    libs.append((abi, os.path.join(abi_dir, f)))

        return libs