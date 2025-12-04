from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Launch browser (visible for demo)

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Go to a page
    try:
        page.goto("https://www.flashscore.com")
    except:
        TimeoutError
        print("Request Timeout")

    # Get and print the page title
    print("Page title:", page.title())

    # Close the browser
    browser.close()

