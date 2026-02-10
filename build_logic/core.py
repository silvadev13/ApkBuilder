import subprocess
import logging

class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: "\033[90m",
        logging.INFO: "\033[94m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[91m",
        logging.CRITICAL: "\033[1;91m",
    }

    TIME_COLOR = "\033[90m"
    RESET = "\033[0m"

    def format(self, record):
        levelname = record.levelname
        asctime = self.formatTime(record, self.datefmt)

        level_color = self.LEVEL_COLORS.get(record.levelno, self.RESET)

        record.levelname = f"{level_color}{levelname}{self.RESET}"
        record.asctime = f"{self.TIME_COLOR}{asctime}{self.RESET}"

        message = super().format(record)

        record.levelname = levelname
        record.asctime = asctime

        return message


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