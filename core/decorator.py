TOOL_REGISTRY = {}


def tool(name, description="", sensitive: bool = False, permission: str = "user"):
    """Register a function as a tool.

    Args:
        name: Tool name used for lookup.
        description: Human-friendly description.
        sensitive: Marks tool as security-sensitive (requires explicit confirmation).
        permission: Minimum permission level required (e.g., 'user' or 'admin').
    """
    def decorator(func):
        TOOL_REGISTRY[name] = {
            "description": description,
            "function": func,
            "sensitive": bool(sensitive),
            "permission": permission,
        }
        return func

    return decorator