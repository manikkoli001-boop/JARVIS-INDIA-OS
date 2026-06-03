import os
import platform
import subprocess
from typing import Optional

from core.decorator import tool

POWER_ACTIONS_ENV_VAR = "JARVIS_ALLOW_POWER_ACTIONS"


def _power_actions_allowed() -> bool:
    return os.environ.get(POWER_ACTIONS_ENV_VAR, "").strip().lower() in {"1", "true", "yes"}


def _windows_command(command: str) -> None:
    subprocess.run(["cmd", "/c", command], shell=False, capture_output=True)


def _power_action_blocked_message(action: str) -> str:
    return (
        f"Power action '{action}' is blocked by safe mode. "
        f"Set {POWER_ACTIONS_ENV_VAR}=1 to allow execution."
    )


@tool(name="system_shutdown", description="Shutdown the system with explicit confirmation.", sensitive=True, permission="admin")
def system_shutdown(confirm: bool = False) -> str:
    if not confirm:
        return "Confirm shutdown by setting confirm=True."
    if not _power_actions_allowed():
        return _power_action_blocked_message("shutdown")
    if platform.system().lower() == "windows":
        _windows_command("shutdown /s /t 0")
        return "System shutdown initiated."
    return "System shutdown is not supported on this platform."


@tool(name="system_restart", description="Restart the system with explicit confirmation.", sensitive=True, permission="admin")
def system_restart(confirm: bool = False) -> str:
    if not confirm:
        return "Confirm restart by setting confirm=True."
    if not _power_actions_allowed():
        return _power_action_blocked_message("restart")
    if platform.system().lower() == "windows":
        _windows_command("shutdown /r /t 0")
        return "System restart initiated."
    return "System restart is not supported on this platform."


@tool(name="system_sleep", description="Put the system to sleep with explicit confirmation.", sensitive=True, permission="admin")
def system_sleep(confirm: bool = False) -> str:
    if not confirm:
        return "Confirm sleep by setting confirm=True."
    if not _power_actions_allowed():
        return _power_action_blocked_message("sleep")
    if platform.system().lower() == "windows":
        _windows_command("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "System sleep initiated."
    return "System sleep is not supported on this platform."


@tool(name="volume_control", description="Control system volume with safety confirmation.", sensitive=True, permission="user")
def volume_control(level: Optional[int] = None, change: Optional[str] = None, confirm: bool = False) -> str:
    if not confirm:
        return "Confirm volume change by setting confirm=True."
    if level is not None:
        return f"Setting volume to {level}%." if 0 <= level <= 100 else "Volume level must be between 0 and 100."
    if change:
        return f"Adjusting volume {change}."
    return "Provide either a level or change direction for volume_control."


@tool(name="brightness_control", description="Adjust screen brightness with safety confirmation.", sensitive=True, permission="user")
def brightness_control(level: Optional[int] = None, change: Optional[str] = None, confirm: bool = False) -> str:
    if not confirm:
        return "Confirm brightness change by setting confirm=True."
    if level is not None:
        return f"Setting brightness to {level}%." if 0 <= level <= 100 else "Brightness level must be between 0 and 100."
    if change:
        return f"Adjusting brightness {change}."
    return "Provide either a level or change direction for brightness_control."
