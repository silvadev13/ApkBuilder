from utils.util import run, get_logger, cmd_is_available
from core.project import Project
import shutil
import os

class Aapt2Task:
    def __init__(self, project: Project):
        self.project = project
        self.android_jar = os.path.join(self.project.sdk_dir, "platforms", f"android-{self.project.target_sdk}", "android.jar")
        self.libs_to_compile = []
    
    def prepare(self):
        aapt2_available = cmd_is_available(self.project.bin_aapt2)
        if not aapt2_available:
            raise Exception("> aapt2 not detected in PATH or SDK build-tools. Please set it in PATH or project configuration.")
        
        get_logger().info("-- Preparing Aapt2")
        self.libs_to_compile = self.project.find_lib_jars()
        bin_dir = self.project.bin_dir
        compiled_res_dir = self.project.compiled_res_dir
        gen_dir = self.project.gen_dir
        if os.path.exists(gen_dir):
            shutil.rmtree(gen_dir)
        
        filtered_libs = []
        for jar in self.libs_to_compile:
            lib_dir = os.path.dirname(jar)
            lib_name = os.path.basename(lib_dir)
            if os.path.exists(os.path.join(compiled_res_dir, lib_name + ".zip")):
                continue
            filtered_libs.append(os.path.abspath(jar))
        self.libs_to_compile = filtered_libs
        
        if os.path.isdir(bin_dir):
            # BOLT OPTIMIZATION: Use os.scandir instead of os.listdir + os.path.join/isdir
            # to avoid stat syscalls and string concatenations during bin_dir cleanup.
            with os.scandir(bin_dir) as entries:
                for entry in entries:
                    if entry.name == "res":
                        continue
                    if entry.is_dir():
                        shutil.rmtree(entry.path)
                    else:
                        os.remove(entry.path)
        
        os.makedirs(bin_dir, exist_ok=True)
        os.makedirs(gen_dir, exist_ok=True)
    
    def compile_libs_aapt2(self):
        out_dir = self.project.compiled_res_dir
        os.makedirs(out_dir, exist_ok=True)

        compiled = []

        for lib in self.libs_to_compile:
            lib_dir = os.path.dirname(lib)
            lib_name = os.path.basename(lib_dir)
            res = os.path.join(lib_dir, "res")
            if not os.path.isdir(res):
                continue
            
            out = os.path.join(out_dir, f"{lib_name}.zip")
            run([
                self.project.bin_aapt2, "compile",
                "--dir", res,
                "-o", out
            ])
            compiled.append(out)

        return compiled
    
    def start(self):
        get_logger().info("-- Compiling resources")
        
        #compile res
        compiled_res_dir = self.project.compiled_res_dir
        os.makedirs(compiled_res_dir, exist_ok=True)
        
        run([
            self.project.bin_aapt2, "compile",
            "--dir", self.project.res_dir,
            "-o", os.path.join(compiled_res_dir, "res.zip")
        ])
        
        #compile libraries
        self.compile_libs_aapt2()
        
        #link res
        args = [
            self.project.bin_aapt2, "link",
            "--allow-reserved-package-id",
            "--no-version-vectors",
            "--no-version-transitions",
            "--auto-add-overlay",
            "--min-sdk-version", str(self.project.min_sdk),
            "--target-sdk-version", str(self.project.target_sdk),
            "--version-code", str(self.project.version_code),
            "--version-name", str(self.project.version_name),
            "-I", self.android_jar,
        ]
        
        assets_dir = self.project.assets_dir
        if assets_dir and os.path.isdir(assets_dir):
            args += ["-A", assets_dir]
        
        #add compiled res
        # BOLT OPTIMIZATION: Use os.scandir to avoid os.listdir list creation and os.path.join calls
        if os.path.isdir(compiled_res_dir):
            with os.scandir(compiled_res_dir) as entries:
                for entry in entries:
                    if entry.is_file() and entry.name.endswith(".zip"):
                        args += ["-R", entry.path]
        
        #use to gen R.java for used libraries
        extra_packages = self.project.get_lib_package_names()
        if extra_packages:
            args += ["--extra-packages", extra_packages]
        
        output_res = os.path.join(self.project.bin_dir, "gen.apk.res")
        r_text = os.path.join(self.project.compiled_res_dir, "R.txt")
        if os.path.exists(r_text):
            os.remove(r_text)
            open(r_text, "w").close()
        
        args += [
            "--java", self.project.gen_dir,
            "--manifest", self.project.manifest_file,
            "-o", output_res,
            "--output-text-symbols", r_text
        ]
        
        run(args)
