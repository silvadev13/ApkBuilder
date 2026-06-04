import logging
import shutil
import os

_logger = None

def get_logger():
    global _logger
    if _logger is None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        )
        _logger = logging.getLogger("cerealicious.build")
    return _logger

def get_bin(name: str) -> str | None:
    """Resolve a binary from PATH. Returns full path or None."""
    return shutil.which(name)

def ensure_dir(path: str):
    """Create directory and all parents if they don't exist."""
    os.makedirs(path, exist_ok=True)

def clean_dir(path: str):
    """Remove and recreate a directory."""
    if os.path.exists(path):
        import shutil as sh
        sh.rmtree(path)
    os.makedirs(path, exist_ok=True)
