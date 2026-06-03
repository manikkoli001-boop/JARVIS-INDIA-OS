import asyncio
from browser_controller import BrowserController


async def main():
    browser_controller = BrowserController()
    try:
        # Open Google and search for "OpenAI"
        await browser_controller.search_google("OpenAI")

        # Print webpage text
        page_text = await browser_controller.get_page_text()
        print("Webpage Text:\n", page_text)

        # Save screenshot
        await browser_controller.screenshot("screenshot.png")
        print("Screenshot saved as screenshot.png")

    finally:
        # Close browser
        await browser_controller.close_browser()
        print("Browser closed.")


if __name__ == "__main__":
    asyncio.run(main())
