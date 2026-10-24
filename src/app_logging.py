import logging
import sys

from src.resource_paths import data_path


def configure_logging() -> None:
    log_path = data_path("UMK.log")
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s %(processName)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )
    if sys.stdout is None:
        sys.stdout = open(log_path, "a", buffering=1)
    if sys.stderr is None:
        sys.stderr = open(log_path, "a", buffering=1)
