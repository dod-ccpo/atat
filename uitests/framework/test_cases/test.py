from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

if __name__ == "__main__":
    # Start the driver
    with webdriver.Chrome() as driver:
        # Open URL
        driver.get("https://seleniumhq.github.io")
        # Setup wait for later
        wait = WebDriverWait(driver, 100)
        # Store the ID of the original window
        original_window = driver.current_window_handle
        # Check we don't have other windows open already
        assert len(driver.window_handles) == 1
        # Click the link which opens in a new window
        driver.find_element_by_css_selector('[href="/documentation"]').click()
        # Wait for the new window or tab
        wait.until(EC.number_of_windows_to_be(2))
        # Loop through until we find a new window handle
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                break
        # Wait for the new tab to finish loading content
        wait.until(EC.title_is("SeleniumHQ Browser Automation"))
