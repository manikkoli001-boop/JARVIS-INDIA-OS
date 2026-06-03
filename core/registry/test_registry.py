from core.decorator import tool, TOOL_REGISTRY


@tool(
    name="hello_tool",
    description="Simple test tool"
)
def hello():
    return "Hello Jarvis"


print(TOOL_REGISTRY)