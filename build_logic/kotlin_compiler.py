from .core import cmd_is_available, run, get_logger, cmd_is_available
from .project import Project
import os

class KotlinCompiler:
    def __init__(self, project: Project):
        self.tools = os.path.abspath("./build_logic/tools")
        self.android_jar = os.path.join(self.tools, "android.jar")
        self.project = project
    
    def prepare(self):
        pass
    
    def start(self):
        kotlin_files = self.project.find_kotlin_files()
        if not kotlin_files:
            return

        get_logger().info("> :app:compileKotlinWithKotlinc")

        kotlinc_available = cmd_is_available("kotlinc")
        if not kotlinc_available:
            error_msg = "> kotlinc not detected in PATH. Please set it in PATH."
            get_logger().error(error_msg)
            raise Exception(error_msg)
        
        
        kotlin_classes_dir = self.project.get_kotlin_classes_dir()
        os.makedirs(kotlin_classes_dir, exist_ok=True)
        
        lib_jars = self.project.find_lib_jars()
        classpath = os.pathsep.join([
            self.android_jar,
            self.project.get_java_classes_dir(),
            *lib_jars
        ])

        
        args = [
            "kotlinc",
            *kotlin_files,
            "-classpath", classpath,
            "-d", self.project.get_kotlin_classes_dir(),
            "-jvm-target", "17"
        ]
        
        run(args)
