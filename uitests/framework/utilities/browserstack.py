import json
from typing import Dict, Optional

from selenium.common.exceptions import WebDriverException


def browserstack_proxy(driver, func):
    """
    Creates a function that can be used to automatically catch Selenium
    errors and turn them into BrowserStack failures.
    """

    def wrapped(*args, **kwargs):
        try:
            # Attempt to call the wrapped function with the arguments
            # passed and return the value
            return func(*args, **kwargs)
        except WebDriverException as e:
            # Specifically for WebDriverExceptions (though this could be made
            # to apply to others) execute a BrowserStack Execution script to
            # set the status to failed with the message from the exception
            driver.execute_script(set_session_status("failed", str(e)))
            # Re-raise the exception so that callers can handle it and update
            # the status again if desired
            raise e
        # All other exceptions are not handled and will be passed up the stack

    # This returns our custom magic function
    return wrapped


class BrowserStackWrapper:
    """
    Wrap a Selenium WebDriver to automatically send errors back to
    BrowserStack.

    This is a basic wrapper for the __getattr__, __setattr__, and __delattr__
    methods so that things can selectively be proxied to an underlying Selenium
    WebDriver fairly transparently. This allows for, for example, automatic error
    handling and reporting back to the BrowserStack API. Theoretically though, this
    could be made more generic to be a general-use error handling Proxy.
    """

    def __init__(self, webdriver):
        object.__setattr__(self, "_webdriver", webdriver)

    def __getattr__(self, name):
        if name == "_webdriver":
            return object.__getattribute__(self, name)
        webdriver = self.__dict__["_webdriver"]
        attr = getattr(webdriver, name)
        if not callable(attr):
            return attr
        return browserstack_proxy(webdriver, attr)

    def __setattr__(self, name, value):
        if name == "_webdriver":
            raise AttributeError("webdriver may not be modified")
        webdriver = self.__dict__["_webdriver"]
        return setattr(webdriver, name, value)

    def __delattr__(self, name: str) -> None:
        if name == "_webdriver":
            raise AttributeError("webdriver may not be modified")
        webdriver = self.__dict__["_webdriver"]
        return delattr(webdriver, name)


def browserstack_command(command_data: Dict) -> str:
    """
    Formats the given command arguments to be passed to Selenium's
    execute_script function.

    :param command_data: The BrowserStack API action info
    """

    json_str = json.dumps(command_data)
    return f"browserstack_executor: {json_str}"


def set_session_name(name: str) -> str:
    """
    Creates the command for setting the session name.

    :param name: The name to use for the session
    :returns: The command to pass to execute_script
    """

    command_data = {"action": "setSessionName", "arguments": {"name": name}}
    return browserstack_command(command_data)


def set_session_status(status: str, reason: Optional[str] = None) -> str:
    """
    Creates the command for settings the session status.

    :param status: The status to set for the session
    :param reason: The reason for the session status
    :returns: The command to pass to execute_script
    """

    if status not in ("passed", "failed"):
        raise ValueError(f"Invalid BrowserStack session status: {status}")

    command_data = {
        "action": "setSessionStatus",
        "arguments": {
            "status": status,
        },
    }
    if reason:
        command_data["arguments"]["reason"] = reason
    return browserstack_command(command_data)
