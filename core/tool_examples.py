import platform
import sys
from typing import Any

from core.decorator import tool


MEMORY_DATA = {
    "user_profile": "Manik is building Jarvis India OS",
    "todo": "Create a tool manager, tool discovery, and execution framework",
    "notes": "Tools are registered automatically using the decorator registry"
}


@tool(
    name="calculator",
    description="Calculate a simple arithmetic expression."
)
def calculator(expression: str) -> str:
    """Evaluate a safe arithmetic expression."""
    allowed_chars = set("0123456789+-*/(). %")
    if not expression or any(char not in allowed_chars for char in expression):
        raise ValueError("Expression contains unsupported characters")

    import ast

    node = ast.parse(expression, mode="eval")

    def _validate(node: ast.AST) -> None:
        if isinstance(node, ast.Expression):
            _validate(node.body)
        elif isinstance(node, ast.BinOp):
            _validate(node.left)
            _validate(node.right)
            if not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.FloorDiv)):
                raise ValueError("Unsupported operator")
        elif isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, (ast.UAdd, ast.USub)):
                raise ValueError("Unsupported unary operator")
            _validate(node.operand)
        elif isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):
                raise ValueError("Only numeric constants are allowed")
        else:
            raise ValueError("Unsupported expression element")

    _validate(node)
    return str(eval(compile(node, filename="<calculator>", mode="eval"), {"__builtins__": {}}))


@tool(
    name="system_info",
    description="Return operating system and Python runtime metadata."
)
def system_info() -> str:
    details = {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "executable": sys.executable,
    }
    return "\n".join(f"{key}: {value}" for key, value in details.items())


@tool(
    name="knowledge_search",
    description="Search the in-memory knowledge store by keyword."
)
def memory_search(query: str) -> str:
    if not query:
        return "Please provide a search query."

    matches = [f"{key}: {value}" for key, value in MEMORY_DATA.items() if query.lower() in key.lower() or query.lower() in value.lower()]
    if not matches:
        return f"No memory entries found for '{query}'."
    return "\n".join(matches)
