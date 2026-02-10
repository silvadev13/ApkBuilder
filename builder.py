from build_logic.aapt2_compiler import AAPT2
from build_logic.binding.generator import GenerateViewBinding
from build_logic.java_compiler import JavaCompiler
from build_logic.d8_compiler import D8
from build_logic.kotlin_compiler import KotlinCompiler
from build_logic import packager, project, core
import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(
        description="A lightweight Android build toolkit for Termux that bundles aapt2, javac, kotlinc, and d8 to compile and sign APKs without Android Studio."
    )

    parser.add_argument(
        "project_path",
        help="Project root directory"
    )
    parser.add_argument(
        "--min-sdk",
        type=int,
        default=21,
        help="Min SDK for Android"
    )
    parser.add_argument(
        "--target-sdk",
        type=int,
        default=34,
        help="Target SDK for Android"
    )
    parser.add_argument(
        "--version-code",
        type=int,
        default=1,
        help="APK version code"
    )
    parser.add_argument(
        "--version-name",
        default="1",
        help="APK version name"
    )
    parser.add_argument(
        "--view-binding",
        type=bool,
        default=False,
        help="Enable view binding in project"
    )

    args = parser.parse_args()

    project_path = os.path.abspath(args.project_path)
    min_sdk = args.min_sdk
    target_sdk = args.target_sdk
    version_code = args.version_code
    version_name = args.version_name
    view_binding = args.view_binding

    proj = project.Project(
        project_path,
        min_sdk,
        target_sdk,
        version_code,
        version_name,
        view_binding
    )

    aapt_task = AAPT2(proj)
    aapt_task.prepare()
    aapt_task.start()
    
    if view_binding:
        gen_view_binding_task = GenerateViewBinding(proj)
        gen_view_binding_task.prepare()
        gen_view_binding_task.start()

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

    core.get_logger().info("Apk built successfully")

if __name__ == "__main__":
    main()
