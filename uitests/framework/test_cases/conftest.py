import json
import os
from enum import Enum
from typing import Dict

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from uitests.framework.utilities import browserstack

LOCAL_ID = os.environ.get("BROWSERSTACK_LOCAL_IDENTIFIER", "")
BUILD_NAME = os.environ["BROWSERSTACK_BUILD_NAME"]

common_caps = {
    "os": "Windows",
    "os_version": "10",
    "browser_version": "latest",
    "resolution": "1920x1080",
    "browserstack.debug": "true",
    "browserstack.sendKeys": "true",
    "build": BUILD_NAME,
}

local_caps = {
    "acceptSslCerts": "true",
    "browserstack.local": "true",
    "browserstack.localIdentifier": LOCAL_ID,
}


class Browser(Enum):
    CHROME = "chrome"
    EDGE = "edge"
    IE = "ie"
    SAFARI = "safari"

    def capabilities(self, local: bool = False) -> Dict[str, str]:
        caps = {"browser": self.value, **common_caps}
        if local:
            caps.update(local_caps)
        return caps

    @property
    def webdriver(self):
        return getattr(webdriver, self.value.title())


class ExecutionType(Enum):
    BROWSERSTACK_REMOTE = "BrowserStackRemote"
    BROWSERSTACK_LOCAL = "BrowserStackLocal"
    LOCAL = "Local"


@pytest.fixture()
def setup(browser: Browser, run_type: ExecutionType):
    """
    Setup the browser compatibility and drivers to use for each

    :param browser: string
    :return: SeleniumWebDriverType
    """
    if run_type is ExecutionType.LOCAL:
        constructor = browser.webdriver
        args = {}
        print(f"Launching in local browser: {browser.value.title()}")
    else:
        user_name = os.environ["BROWSERSTACK_USERNAME"]
        access_key = os.environ["BROWSERSTACK_ACCESS_KEY"]
        constructor = webdriver.Remote
        args = {
            "command_executor": f"https://{user_name}:{access_key}@hub-cloud.browserstack.com/wd/hub",
            "desired_capabilities": browser.capabilities(
                local=(run_type is ExecutionType.BROWSERSTACK_LOCAL)
            ),
        }

    with constructor(**args) as driver:
        if run_type is not ExecutionType.LOCAL:
            driver = browserstack.BrowserStackWrapper(driver)
        yield driver


def pytest_addoption(parser):
    parser.addoption(
        "--browser", help="The name of the browser to use", default=Browser.CHROME.value
    )
    parser.addoption(
        "--run-type",
        help="How to run the tests: BrowserStackLocal, BrowserStackRemote, Local",
        default=ExecutionType.LOCAL.value,
    )


@pytest.fixture()
def browser(request) -> Browser:
    return Browser(request.config.getoption("--browser"))


@pytest.fixture()
def run_type(request) -> ExecutionType:
    return ExecutionType(request.config.getoption("--run-type"))
