from build_logic import aapt2_compiler, java_compiler, kotlin_compiler, d8_compiler, packager, project
from build_logic.core import get_logger
import os

proj = project.Project(os.path.abspath("test_apk"), 21, 34, 1, "1")
aapt_task = aapt2_compiler.AAPT2(proj)
aapt_task.prepare()
aapt_task.start()

java_task = java_compiler.JAVA(proj)
java_task.prepare()
java_task.start()

kotlin_task = kotlin_compiler.KOTLIN(proj)
kotlin_task.prepare()
kotlin_task.start()

d8_task = d8_compiler.D8(proj)
d8_task.prepare()
d8_task.start()

packager_task = packager.APK(proj)
packager_task.prepare()
packager_task.start()

get_logger().info("Apk builded successfully")