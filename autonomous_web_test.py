import asyncio
from browser_controller import BrowserController


async def main():
    browser_controller = BrowserController()
    try:
        # Open Google and search for "OpenAI GPT-5"
        await browser_controller.search_google("OpenAI GPT-5")

        # Click the first result
        await browser_controller.click_text('OpenAI')

        # Extract all links
        links = await browser_controller.get_links()
        print("Extracted Links:\n", links)

        # Save screenshot
        await browser_controller.screenshot("autonomous_test_screenshot.png")
        print("Screenshot saved as autonomous_test_screenshot.png")

        # Print webpage text
        page_text = await browser_controller.get_page_text()
        print("Webpage Text:\n", page_text)

    finally:
        # Close browser
        await browser_controller.close_browser()
        print("Browser closed.")


if __name__ == "__main__":
    asyncio.run(main())