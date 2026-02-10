from .core import run, get_logger
from .project import Project
import os

class D8:
    def __init__(self, project: Project):
        self.tools = os.path.abspath("./build_logic/tools")
        self.aapt2 = os.path.join(self.tools, "aapt2")
        self.android_jar = os.path.join(self.tools, "android.jar")
        self.r8 = os.path.join(self.tools, "r8-8.13.19.jar")
        self.project = project
    
    def prepare(self):
        pass
    
    def start(self):
        get_logger().info("> :app:compileDexWithD8")
        
        java_classes_files = self.project.find_files(self.project.get_java_classes_dir(), ".class")
        kotlin_classes_files = self.project.find_files(self.project.get_kotlin_classes_dir(), ".class")
        all_class_files = java_classes_files + kotlin_classes_files
        
        if not all_class_files:
            get_logger().error("> No class files found")
            return
        
        args = [
            "java",
            "-cp", self.r8,
            "com.android.tools.r8.D8",
            "--release",
            "--min-api", str(self.project.get_min_sdk()),
            "--lib", self.android_jar,
            "--output", self.project.get_bin_dir(),
            *all_class_files,
            *self.project.find_lib_jars()
        ]
    
        run(args)