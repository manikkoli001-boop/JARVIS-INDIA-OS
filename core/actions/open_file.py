import os
import platform
import subprocess
from pathlib import Path

from core.decorator import tool


@tool(name="open_file", description="Open a file in the default system application.")
def open_file(file_path: str) -> str:
    if not file_path:
        return "File path is required."

    path = Path(file_path).expanduser()
    if not path.exists():
        return f"File not found: {file_path}"

    try:
        if platform.system().lower() == "windows":
            os.startfile(str(path))
        elif platform.system().lower() == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return f"Opening file: {path}"
    except Exception as exc:
        return f"Unable to open file {file_path}: {exc}"
