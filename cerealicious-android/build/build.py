#!/usr/bin/env python3
"""
Cerealicious Android Build Pipeline
Usage:
  python build.py [--project <dir>] [--clean] [--release]
"""

import argparse
import os
import subprocess
import sys

# Make sure utils is importable when running from build/
sys.path.insert(0, os.path.dirname(__file__))

from project import Project
from utils.util import get_logger, ensure_dir, clean_dir

log = get_logger()


def run(cmd: list[str], desc: str):
    log.info(f"── {desc}")
    log.info("   " + " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout.strip():
        log.info(result.stdout.strip())
    if result.returncode != 0:
        log.error(result.stderr.strip())
        raise RuntimeError(f"Step failed: {desc}")
    return result


# ── Step 1: Compile resources with aapt2 ─────────────────────────────────────

def step_compile_res(p: Project):
    ensure_dir(p.compiled_res_dir)
    res_files = []
    for root, _, files in os.walk(p.res_dir):
        for f in files:
            res_files.append(os.path.join(root, f))

    if not res_files:
        log.warning("-- no resource files found, skipping aapt2 compile")
        return

    for res_file in res_files:
        run([
            p.bin_aapt2, "compile",
            res_file,
            "-o", p.compiled_res_dir,
        ], f"aapt2 compile: {os.path.basename(res_file)}")

    log.info(f"✓ Compiled {len(res_files)} resource files")


# ── Step 2: Link resources with aapt2 ────────────────────────────────────────

def step_link_res(p: Project):
    ensure_dir(p.gen_dir)

    flat_files = [
        os.path.join(p.compiled_res_dir, f)
        for f in os.listdir(p.compiled_res_dir)
        if f.endswith(".flat")
    ]

    cmd = [
        p.bin_aapt2, "link",
        "--proto-format",
        "-o", os.path.join(p.output_dir, "resources.ap_"),
        "--manifest", p.manifest_file,
        "-I", p.android_jar(),
        "--java", p.gen_dir,
        "--auto-add-overlay",
        "--min-sdk-version", str(p.min_sdk),
        "--target-sdk-version", str(p.target_sdk),
        "--version-code", str(p.version_code),
        "--version-name", str(p.version_name),
    ]

    # Include assets if they exist
    if os.path.isdir(p.assets_dir):
        cmd += ["-A", p.assets_dir]

    # Include library packages
    lib_packages = p.get_lib_package_names()
    if lib_packages:
        cmd += ["--extra-packages", lib_packages]

    cmd += flat_files

    run(cmd, "aapt2 link resources")
    log.info("✓ Resources linked")


# ── Step 3: Generate View Bindings ───────────────────────────────────────────

def step_view_binding(p: Project):
    if not p.enable_view_binding:
        log.info("-- view binding disabled, skipping")
        return

    ensure_dir(p.view_binding_dir)

    layout_dir = os.path.join(p.res_dir, "layout")
    if not os.path.isdir(layout_dir):
        log.warning("-- no layout dir found, skipping view binding")
        return

    # Generate a simple binding class for each layout XML
    for layout_file in os.listdir(layout_dir):
        if not layout_file.endswith(".xml"):
            continue

        base = layout_file.replace(".xml", "")
        class_name = "".join(w.capitalize() for w in base.split("_")) + "Binding"

        binding_src = f"""\
package {p.package_name}.databinding;

import android.view.View;
import androidx.annotation.NonNull;

/** Auto-generated View Binding for {layout_file} */
public final class {class_name} {{

    @NonNull
    public final View root;

    private {class_name}(@NonNull View root) {{
        this.root = root;
    }}

    @NonNull
    public static {class_name} bind(@NonNull View rootView) {{
        return new {class_name}(rootView);
    }}
}}
"""
        out_pkg_dir = os.path.join(
            p.view_binding_dir,
            p.package_name.replace(".", os.sep),
            "databinding",
        )
        ensure_dir(out_pkg_dir)
        with open(os.path.join(out_pkg_dir, f"{class_name}.java"), "w") as f:
            f.write(binding_src)

    log.info("✓ View bindings generated")


# ── Step 4: Compile Kotlin sources ───────────────────────────────────────────

def step_compile_kotlin(p: Project):
    kt_files = p.find_kotlin_files()
    if not kt_files:
        log.info("-- no Kotlin files found, skipping kotlinc")
        return

    ensure_dir(p.kotlin_classes_dir)

    classpath_parts = [p.android_jar()] + p.find_lib_jars()
    classpath = os.pathsep.join(classpath_parts)

    run([
        p.bin_kotlinc,
        *kt_files,
        "-classpath", classpath,
        "-d", p.kotlin_classes_dir,
        "-jvm-target", str(p.java_version),
        "-no-stdlib",
    ], f"kotlinc ({len(kt_files)} files)")

    log.info(f"✓ Compiled {len(kt_files)} Kotlin files")


# ── Step 5: Compile Java sources ─────────────────────────────────────────────

def step_compile_java(p: Project):
    # Gather all Java sources: main + generated (R.java, bindings)
    java_files = (
        p.find_java_files()
        + p.find_java_files(p.gen_dir)
        + (p.find_java_files(p.view_binding_dir) if p.enable_view_binding else [])
    )

    if not java_files:
        log.warning("-- no Java files found")
        return

    ensure_dir(p.java_classes_dir)

    classpath_parts = (
        [p.android_jar(), p.kotlin_classes_dir]
        + p.find_lib_jars()
    )
    classpath = os.pathsep.join(classpath_parts)

    run([
        p.bin_javac,
        "-source", str(p.java_version),
        "-target", str(p.java_version),
        "-classpath", classpath,
        "-d", p.java_classes_dir,
        "-encoding", "UTF-8",
        *java_files,
    ], f"javac ({len(java_files)} files)")

    log.info(f"✓ Compiled {len(java_files)} Java files")


# ── Step 6: Dex with d8 ──────────────────────────────────────────────────────

def step_dex(p: Project):
    ensure_dir(p.dex_dir)

    # Collect all .class files from java + kotlin output dirs
    class_dirs = [p.java_classes_dir, p.kotlin_classes_dir]
    class_files = []
    for d in class_dirs:
        if os.path.isdir(d):
            for root, _, files in os.walk(d):
                for f in files:
                    if f.endswith(".class"):
                        class_files.append(os.path.join(root, f))

    lib_jars = p.find_lib_jars()

    run([
        p.bin_d8,
        *class_files,
        *lib_jars,
        "--output", p.dex_dir,
        "--min-api", str(p.min_sdk),
        "--lib", p.android_jar(),
    ], f"d8 dex ({len(class_files)} classes)")

    log.info("✓ DEX compiled")


# ── Step 7: Package APK ──────────────────────────────────────────────────────

def step_package(p: Project):
    apk_name = f"cerealicious-{p.build_type}-unsigned.apk"
    apk_path = os.path.join(p.output_dir, apk_name)

    # Start from the linked resources archive
    resources_ap = os.path.join(p.output_dir, "resources.ap_")
    if not os.path.exists(resources_ap):
        raise FileNotFoundError(f"resources.ap_ not found — did aapt2 link succeed?")

    import shutil
    shutil.copy2(resources_ap, apk_path)

    # Add DEX files using zip
    import zipfile
    dex_files = p.find_dex_files()
    native_libs = p.find_native_libs()

    with zipfile.ZipFile(apk_path, "a", compression=zipfile.ZIP_DEFLATED) as apk:
        for dex_file in dex_files:
            apk.write(dex_file, os.path.basename(dex_file))
            log.info(f"   + {os.path.basename(dex_file)}")

        for abi, so_file in native_libs:
            arcname = f"lib/{abi}/{os.path.basename(so_file)}"
            apk.write(so_file, arcname)
            log.info(f"   + {arcname}")

    p._unsigned_apk = apk_path
    log.info(f"✓ APK packaged: {apk_path}")


# ── Step 8: Sign APK ─────────────────────────────────────────────────────────

def step_sign(p: Project):
    unsigned = getattr(p, "_unsigned_apk", None)
    if not unsigned:
        raise RuntimeError("No unsigned APK path found — packaging step may have failed")

    signed_name = f"cerealicious-{p.build_type}.apk"
    signed_path = os.path.join(p.output_dir, signed_name)

    if p.build_type == "debug":
        # Use apksigner with a debug keystore
        debug_ks = os.path.join(
            os.path.expanduser("~"), ".android", "debug.keystore"
        )
        if not os.path.exists(debug_ks):
            log.warning(f"-- debug keystore not found at {debug_ks}, skipping sign")
            return

        run([
            p.bin_apksigner, "sign",
            "--ks", debug_ks,
            "--ks-pass", "pass:android",
            "--key-pass", "pass:android",
            "--ks-key-alias", "androiddebugkey",
            "--out", signed_path,
            unsigned,
        ], "apksigner (debug)")

    else:
        if not os.path.exists(p.keystore_file):
            raise FileNotFoundError(f"-- release keystore not found: {p.keystore_file}")

        run([
            p.bin_apksigner, "sign",
            "--ks", p.keystore_file,
            "--ks-pass", f"pass:{p.keystore_store_pass}",
            "--key-pass", f"pass:{p.keystore_key_pass}",
            "--ks-key-alias", p.keystore_alias,
            "--out", signed_path,
            unsigned,
        ], "apksigner (release)")

    log.info(f"✓ APK signed: {signed_path}")
    return signed_path


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Cerealicious Android Build")
    parser.add_argument("--project", default="..", help="Path to project root (default: ..)")
    parser.add_argument("--clean",   action="store_true", help="Clean build output before building")
    parser.add_argument("--release", action="store_true", help="Force release build type")
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project)
    log.info(f"Building Cerealicious from: {project_dir}")

    p = Project(project_dir)

    if args.release:
        p.build_type = "release"
        log.info("-- overriding build type to: release")

    if args.clean:
        log.info("-- cleaning build output")
        clean_dir(p.output_dir)

    log.info(f"Build type : {p.build_type}")
    log.info(f"Package    : {p.package_name}")
    log.info(f"Version    : {p.version_name} ({p.version_code})")
    log.info(f"SDK target : {p.target_sdk}  (min: {p.min_sdk})")
    log.info("")

    steps = [
        ("Compile resources",   lambda: step_compile_res(p)),
        ("Link resources",      lambda: step_link_res(p)),
        ("View Binding",        lambda: step_view_binding(p)),
        ("Compile Kotlin",      lambda: step_compile_kotlin(p)),
        ("Compile Java",        lambda: step_compile_java(p)),
        ("DEX",                 lambda: step_dex(p)),
        ("Package APK",         lambda: step_package(p)),
        ("Sign APK",            lambda: step_sign(p)),
    ]

    for name, fn in steps:
        log.info(f"━━ {name} {'━' * (40 - len(name))}")
        try:
            fn()
        except Exception as e:
            log.error(f"✗ {name} failed: {e}")
            sys.exit(1)

    log.info("")
    log.info("✅  Build complete!")
    log.info(f"   Output: {p.output_dir}/cerealicious-{p.build_type}.apk")


if __name__ == "__main__":
    main()
