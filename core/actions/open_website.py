import webbrowser

from core.decorator import tool


@tool(name="open_website", description="Open a website URL in the default browser.")
def open_website(url: str) -> str:
    if not url:
        return "A website URL is required."

    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    webbrowser.open(url)
    return f"Opening website: {url}"
