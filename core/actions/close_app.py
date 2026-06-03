import os
import platform
import subprocess
from typing import Optional

from core.decorator import tool


@tool(name="close_app", description="Close a running application by process name.")
def close_app(process_name: str, force: Optional[bool] = False) -> str:
    if not process_name:
        return "Process name is required."

    system = platform.system().lower()
    try:
        if system == "windows":
            command = ["taskkill", "/IM", process_name]
            if force:
                command.append("/F")
            subprocess.run(command, shell=False, capture_output=True)
        elif system in {"darwin", "linux"}:
            signal = "-9" if force else "-15"
            subprocess.run(["pkill", signal, process_name], shell=False, capture_output=True)
        else:
            return f"Closing apps is not supported on {system}."
        return f"Attempted to close {process_name}."
    except Exception as exc:
        return f"Unable to close {process_name}: {exc}"
