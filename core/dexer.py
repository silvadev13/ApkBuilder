from utils.util import run, get_logger, cmd_is_available
from core.project import Project
import os

class Task:
    def __init__(self, project: Project):
        self.project = project
        self.android_jar = os.path.join(self.project.sdk_dir, "platforms", f"android-{self.project.target_sdk}", "android.jar")
        self.classpath = None
    
    def prepare(self):
        d8_available = cmd_is_available(self.project.bin_d8)
        if not d8_available:
            raise Exception("-- d8 not detected in PATH or SDK build-tools. Please set it in PATH.")
        
        if not os.path.exists(self.project.dex_dir):
            os.makedirs(self.project.dex_dir)
        
        for library in self.project.find_lib_jars():
            library_dir = os.path.dirname(library)
            dex_files = self.project.find_files(library_dir, ".dex")
            if not dex_files:
                self.__dex_library(library)
    
    def start(self):
        get_logger().info("-- Dexing with D8")
        
        java_classes_files = self.project.find_files(self.project.java_classes_dir, ".class")
        kotlin_classes_files = self.project.find_files(self.project.kotlin_classes_dir, ".class")
        all_class_files = java_classes_files + kotlin_classes_files
        
        if not all_class_files:
            raise Exception("-- no class files found")
        
        run([
            self.project.bin_d8,
            f"--{self.project.build_type}",
            "--min-api", str(self.project.min_sdk),
            "--lib", self.android_jar,
            "--output", self.project.dex_dir,
            *all_class_files,
        ])
    
    def __dex_library(self, library_path):
        library_dir = os.path.dirname(library_path)
        
        get_logger().info(f"-- Generating a dex file to {library_dir}")
        
        run([
            self.project.bin_d8,
            f"--{self.project.build_type}",
            "--min-api", str(self.project.min_sdk),
            "--lib", self.android_jar,
            "--output", library_dir,
            library_path,
            *self.__get_classpath()
        ])
    
    def __get_classpath(self):
        # BOLT OPTIMIZATION: Cache classpath list (including empty list when no
        # library jars exist) so __get_classpath does not re-query find_lib_jars().
        if self.classpath is not None:
            return self.classpath
    
        self.classpath = []
        for library in self.project.find_lib_jars():
            self.classpath.extend(["--classpath", library])
    
        return self.classpath
