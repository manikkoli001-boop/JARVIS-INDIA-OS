import os
import platform
import subprocess
from typing import Any

from core.decorator import tool


@tool(name="open_app", description="Open an application by name or path.")
def open_app(application_name: str) -> str:
    if not application_name:
        return "Application name is required."

    system = platform.system().lower()
    try:
        if os.path.isfile(application_name):
            if system == "windows":
                os.startfile(application_name)
            else:
                subprocess.Popen(["open" if system == "darwin" else "xdg-open", application_name])
            return f"Opening {application_name}."

        if system == "windows":
            subprocess.Popen(["cmd", "/c", "start", "", application_name], shell=False)
        elif system == "darwin":
            subprocess.Popen(["open", "-a", application_name])
        else:
            subprocess.Popen([application_name])
        return f"Attempting to open {application_name}."
    except Exception as exc:
        return f"Unable to open {application_name}: {exc}"
