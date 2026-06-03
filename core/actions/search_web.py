import urllib.parse
import webbrowser

from core.decorator import tool


@tool(name="search_web", description="Search the web for a query using the default browser.")
def search_web(query: str) -> str:
    if not query:
        return "A search query is required."

    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded}"
    webbrowser.open(url)
    return f"Searching the web for: {query}"
