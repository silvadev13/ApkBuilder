from utils.color_formatter import ColorFormatter
import os
import subprocess
import logging
import shutil

handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter(
    "[%(asctime)s] [%(levelname)s] %(message)s"
))

log = logging.getLogger("builder")
log.setLevel(logging.INFO)
log.addHandler(handler)
log.propagate = False

def run(cmd):
    subprocess.check_call(
        cmd,
        stdout=subprocess.DEVNULL
    )

def get_logger():
    return log

def get_bin(cmd):
    return shutil.which(cmd)

def cmd_is_available(cmd):
    # BOLT OPTIMIZATION: Use shutil.which instead of os.system("which ...")
    # to avoid subshell process fork overhead (~20x faster) when checking binary availability.
    return shutil.which(cmd) is not None
