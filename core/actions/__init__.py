"""Desktop and system action tools for Jarvis."""

from core.actions.close_app import close_app
from core.actions.open_app import open_app
from core.actions.open_file import open_file
from core.actions.open_folder import open_folder
from core.actions.open_website import open_website
from core.actions.search_web import search_web
from core.actions.system_control import (
    brightness_control,
    system_restart,
    system_shutdown,
    system_sleep,
    volume_control,
)

__all__ = [
    "open_app",
    "close_app",
    "open_file",
    "open_folder",
    "search_web",
    "open_website",
    "system_shutdown",
    "system_restart",
    "system_sleep",
    "volume_control",
    "brightness_control",
]
