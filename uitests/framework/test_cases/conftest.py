import datetime
import os
import pytest

from selenium import webdriver

# buildName = datetime.datetime.now().strftime('Smoke Test: ' + '%m/%d/%y')
buildName = "Work in Progress"

chrome = {
    "os_version": "10",
    "os": "Windows",
    "browser": "chrome",  # Edge  Chrome  IE
    "browser_version": "89.0",  # 88.0  89.0    11.0
    "resolution": "1920x1080",
    "browserstack.sendKeys": "true",
    "browserstack.debug": "true",
    "build": buildName,  # Your tests will be organized within this build
}
edge = {
    "os_version": "10",
    "os": "Windows",
    "browser": "edge",  # Edge  Chrome  IE
    "browser_version": "88.0",  # 88.0  89.0    11.0
    "resolution": "1920x1080",
    "browserstack.sendKeys": "true",
    "browserstack.debug": "true",
    "build": buildName,  # Your tests will be organized within this build
}
ie = {
    "os_version": "10",
    "os": "Windows",
    "browser": "ie",  # Edge  Chrome  IE
    "browser_version": "11.0",  # 88.0  89.0    11.0
    "resolution": "1920x1080",
    "browserstack.sendKeys": "true",
    "browserstack.debug": "true",
    "build": buildName,  # Your tests will be organized within this build
}

allBrowsers = [
    {
        "os_version": "10",
        "os": "Windows",
        "browser": "ie",  # Edge  Chrome  IE
        "browser_version": "11.0",  # 88.0  89.0    11.0
        "resolution": "1920x1080",
        "browserstack.sendKeys": "true",
        "browserstack.debug": "true",
        "build": "parallel test #4",  # Your tests will be organized within this build
    },
    {
        "os_version": "10",
        "os": "Windows",
        "browser": "edge",  # Edge  Chrome  IE
        "browser_version": "88.0",  # 88.0  89.0    11.0
        "resolution": "1920x1080",
        "browserstack.sendKeys": "true",
        "browserstack.debug": "true",
        "build": "parallel test #4",  # Your tests will be organized within this build
    },
    {
        "os_version": "10",
        "os": "Windows",
        "browser": "chrome",  # Edge  Chrome  IE
        "browser_version": "89.0",  # 88.0  89.0    11.0
        "resolution": "1920x1080",
        "browserstack.sendKeys": "true",
        "browserstack.debug": "true",
        "build": "parallel test #4",  # Your tests will be organized within this build
    },
]


@pytest.fixture()
def setup(browser):
    if browser is None:
        browser = "chrome-local"

    address = os.getenv("BrowserStackAPI")
    if browser == "chrome":
        driver = webdriver.Remote(command_executor=address, desired_capabilities=chrome)
        print("Launching Chrome Browser.....")
    elif browser == "edge":
        driver = webdriver.Remote(command_executor=address, desired_capabilities=edge)
        print("Launching Edge Browser.....")
    elif browser == "ie":
        driver = webdriver.Remote(command_executor=address, desired_capabilities=ie)
        print("Launching IE 11 Browser.....")
    elif browser == "all":
        driver = webdriver.Remote(
            command_executor=address, desired_capabilities=allBrowsers
        )
        print("Launching IE 11 Browser.....")
    # elif browser == 'firefox':
    #     driver = webdriver.Remote(
    #         command_executor=address,
    #         desired_capabilities=firefox)
    #     print("Launching Firefox Browser.....")
    elif browser == "chrome-local":
        driver = webdriver.Chrome()
        print("Launching in default browser: Chrome")
    else:
        print("Please select a browser, Example: --browser chrome-local")
    return driver


def pytest_addoption(parser):  # This will get the value from command line or hooks
    parser.addoption("--browser")


@pytest.fixture()  # This will return th browser value to setup method
def browser(request):
    return request.config.getoption("--browser")
