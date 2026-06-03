import os
import platform
import subprocess
from pathlib import Path

from core.decorator import tool


@tool(name="open_folder", description="Open a folder in the operating system file explorer.")
def open_folder(folder_path: str) -> str:
    if not folder_path:
        return "Folder path is required."

    path = Path(folder_path).expanduser()
    if not path.is_dir():
        return f"Folder not found: {folder_path}"

    try:
        if platform.system().lower() == "windows":
            os.startfile(str(path))
        elif platform.system().lower() == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return f"Opening folder: {path}"
    except Exception as exc:
        return f"Unable to open folder {folder_path}: {exc}"
