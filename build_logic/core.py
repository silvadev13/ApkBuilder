from color_formatter import ColorFormatter
import os
import subprocess
import logging

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

def cmd_is_available(cmd):
    isa = os.system(f"which {cmd} > /dev/null") == 0
    return isa
