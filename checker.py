import subprocess
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("install.log"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("installer")


def pkg_installed(pkg_name):
    result = subprocess.run(
        ["pkg", "list-installed"],
        capture_output=True,
        text=True
    )
    return pkg_name in result.stdout


def pip_installed(pkg_name):
    return subprocess.run(
        [sys.executable, "-m", "pip", "show", pkg_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ).returncode == 0


def ask_install(name, kind):
    answer = input(f"{kind} '{name}' not found. Install? (y/n): ").strip().lower()

    if answer in ("y", "yes"):
        return True
    if answer in ("n", "no"):
        return False

    log.error("Invalid answer. Canceling operation.")
    return False


def ensure_pkg(pkg_name):
    if pkg_installed(pkg_name):
        log.info(f"pkg {pkg_name} already installed")
        return

    log.warning(f"pkg {pkg_name} not found")

    if not ask_install(pkg_name, "pkg"):
        log.info("Operation canceled by user")
        return

    log.info(f"Installing pkg {pkg_name}")
    proc = subprocess.run(
        ["pkg", "install", "-y", pkg_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if proc.returncode == 0:
        log.info(f"pkg {pkg_name} installed successfully")
    else:
        log.error(proc.stderr)
        raise RuntimeError(proc.stderr)


def ensure_pip(pkg_name):
    if pip_installed(pkg_name):
        log.info(f"pip {pkg_name} already installed")
        return

    log.warning(f"pip {pkg_name} not found")

    if not ask_install(pkg_name, "pip"):
        log.info("Operation canceled by user")
        return

    log.info(f"Installing pip package {pkg_name}")
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "install", pkg_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if proc.returncode == 0:
        log.info(f"pip {pkg_name} installed successfully")
    else:
        log.error(proc.stderr)
        raise RuntimeError(proc.stderr)