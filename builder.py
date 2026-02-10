from build_logic.aapt2_compiler import AAPT2
from build_logic.java_compiler import JavaCompiler
from build_logic.d8_compiler import D8
from build_logic.kotlin_compiler import KotlinCompiler
from build_logic import  packager, project, core
import os

proj = project.Project(os.path.abspath("test_apk"), 21, 34, 1, "1")
aapt_task = AAPT2(proj)
aapt_task.prepare()
aapt_task.start()

java_task = JavaCompiler(proj)
java_task.prepare()
java_task.start()

kotlin_task = KotlinCompiler(proj)
kotlin_task.prepare()
kotlin_task.start()

d8_task = D8(proj)
d8_task.prepare()
d8_task.start()

packager_task = packager.APK(proj)
packager_task.prepare()
packager_task.start()

core.get_logger().info("Apk builded successfully")
