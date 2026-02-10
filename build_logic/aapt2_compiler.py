from .core import run, get_logger, cmd_is_available
from .project import Project
import shutil
import os

class AAPT2:
    def __init__(self, project: Project):
        self.tools = os.path.abspath("./build_logic/tools")
        self.android_jar = os.path.join(self.tools, "android.jar")
        self.project = project
        self.libs_to_compile = []
    
    def prepare(self):
        get_logger().info("> :app:preparingAAPT2")
        self.libs_to_compile = self.project.find_lib_jars()
        bin_dir = self.project.get_bin_dir()
        compiled_res_dir = self.project.get_compiled_res_dir()
        gen_dir = self.project.get_gen_dir()
        if os.path.exists(gen_dir):
            shutil.rmtree(gen_dir)
        
        filtered_libs = []
        for jar in self.libs_to_compile:
            lib_dir = os.path.dirname(jar)
            lib_name = os.path.basename(lib_dir)
            if os.path.exists(os.path.join(compiled_res_dir, lib_name + ".zip")):
                # remove the library from the list so it wont get compiled
                #get_logger().info(f"> :app:removingLibraryToSpeedUp {lib_name}")
                continue
            filtered_libs.append(os.path.abspath(jar))
        self.libs_to_compile = filtered_libs
        
        if os.path.isdir(bin_dir):
            for child in os.listdir(bin_dir):
                if child == "res":
                    continue
                
                path = os.path.join(bin_dir, child)
                
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
        
        os.makedirs(bin_dir, exist_ok=True)
        os.makedirs(gen_dir, exist_ok=True)
    
    def compile_libs_aapt2(self):
        out_dir = self.project.get_compiled_res_dir()
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
                "aapt2", "compile",
                "--dir", res,
                "-o", out
            ])
            compiled.append(out)

        return compiled
    
    def start(self):
        aapt2_available = cmd_is_available("aapt2")
        if not aapt2_available:
            error_msg = "> aapt2 not detected in PATH. Please set it in PATH."
            get_logger().error(error_msg)
            raise Exception(error_msg)
        
        get_logger().info("> :app:compilingResources")
        
        #compile res
        compiled_res_dir = self.project.get_compiled_res_dir()
        os.makedirs(compiled_res_dir, exist_ok=True)
        
        run([
            "aapt2", "compile",
            "--dir", self.project.get_res_dir(),
            "-o", os.path.join(compiled_res_dir, "res.zip")
        ])
        
        #compile libraries
        self.compile_libs_aapt2()
        
        #link res
        args = [
            "aapt2", "link",
            "--allow-reserved-package-id",
            "--no-version-vectors",
            "--no-version-transitions",
            "--auto-add-overlay",
            "--min-sdk-version", str(self.project.get_min_sdk()),
            "--target-sdk-version", str(self.project.get_target_sdk()),
            "--version-code", str(self.project.get_version_code()),
            "--version-name", str(self.project.get_version_name()),
            "-I", self.android_jar,
        ]
        
        assets_dir = self.project.get_assets_dir()
        if assets_dir and os.path.isdir(assets_dir):
            args += ["-A", assets_dir]
        
        #add compiled res
        for f in os.listdir(compiled_res_dir):
            full = os.path.join(compiled_res_dir, f)
            if f.endswith(".zip"):
                args += ["-R", full]
        
        #use to gen R.java for used libraries
        extra_packages = self.project.get_lib_package_names()
        if extra_packages:
            args += ["--extra-packages", extra_packages]
        
        output_res = os.path.join(self.project.get_bin_dir(), "gen.apk.res")
        r_text = os.path.join(self.project.get_compiled_res_dir(), "R.txt")
        if os.path.exists(r_text):
            os.remove(r_text)
            open(r_text, "w").close()
        
        args += [
            "--java", self.project.get_gen_dir(),
            "--manifest", self.project.get_manifest_file(),
            "-o", output_res,
            "--output-text-symbols", r_text
        ]
        
        run(args)