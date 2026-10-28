
from collections.abc import Generator

import pytest
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver


@pytest.fixture(scope="function")
def driver() -> Generator[WebDriver, None, None]:
    browser = webdriver.Chrome()
    browser.maximize_window()

    try:
        yield browser
    finally:
        browser.quit()
