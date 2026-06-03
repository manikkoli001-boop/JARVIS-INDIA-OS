import asyncio
from browser_controller import BrowserController


async def main():
    """
    Test script for BrowserController.
    Opens google.com, searches for "OpenAI", and closes the browser.
    """
    browser_controller = BrowserController()
    
    try:
        # Open Google
        await browser_controller.open_url("https://www.google.com")
        print("Opened Google. Searching for 'OpenAI'...")
        
        # Search for "OpenAI"
        await browser_controller.search_google("OpenAI")
        
        # Print webpage text
        page_text = await browser_controller.get_page_text()
        print("Webpage Text:\n", page_text)
        
        # Save screenshot
        await browser_controller.screenshot("screenshot.png")
        print("Screenshot saved as screenshot.png")

    finally:
        # Ensure browser is closed even if an error occurs
        await browser_controller.close_browser()
        print("Browser closed.")


if __name__ == "__main__":
    asyncio.run(main())
