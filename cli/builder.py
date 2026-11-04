from core.binding.generator import GenerateViewBinding
from core import resources, dexer, compiler, packager, project
from utils.util import get_logger
import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(
        description="A lightweight Android Project builder CLI."
    )

    parser.add_argument(
        "project_path",
        help="Project root directory"
    )

    args = parser.parse_args()

    project_path = os.path.abspath(args.project_path)

    try:
        proj = project.Project(project_path)
    except Exception as e:
        get_logger().error(e)
        sys.exit(1)

    aapt_task = resources.Aapt2Task(proj)
    aapt_task.prepare()
    aapt_task.start()
    
    if proj.enable_view_binding:
        gen_view_binding_task = GenerateViewBinding(proj)
        gen_view_binding_task.prepare()
        gen_view_binding_task.start()

    java_task = compiler.JavaTask(proj)
    java_task.prepare()
    java_task.start()

    kotlin_task = compiler.KotlinTask(proj)
    kotlin_task.prepare()
    kotlin_task.start()

    d8_task = dexer.Task(proj)
    d8_task.prepare()
    d8_task.start()

    packager_task = packager.Task(proj)
    packager_task.prepare()
    packager_task.start()

    get_logger().info("Apk built successfully")

if __name__ == "__main__":
    main()
