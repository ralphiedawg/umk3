import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parents[1]
    return base_path / relative_path


def data_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False):
        base_path = Path.home() / "Library" / "Application Support" / "UMK"
    else:
        base_path = Path.cwd()
    path = base_path / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
