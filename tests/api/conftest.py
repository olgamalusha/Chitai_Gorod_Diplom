
import json
from pathlib import Path
from urllib.parse import unquote

import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture(scope="session")
def guest_token() -> str:
    config_path = Path(__file__).resolve().parents[2] / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    driver = webdriver.Chrome()

    try:
        driver.get(config["site_url"])

        cookie = WebDriverWait(driver, 15).until(
            lambda browser: browser.get_cookie("access-token")
        )
    finally:
        driver.quit()

    assert cookie is not None

    token = unquote(cookie["value"]).removeprefix("Bearer ")

    assert token

    return token
