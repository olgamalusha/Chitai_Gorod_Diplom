
import json
from pathlib import Path

import allure
import pytest
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.ui
@allure.title("UI-03 — Переход в категорию художественной литературы")
@allure.story("Каталог книг")
def test_open_fiction_category(driver: WebDriver) -> None:
    config_path = Path(__file__).resolve().parents[2] / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    wait = WebDriverWait(driver, 15)

    catalog_locator = (
        By.CSS_SELECTOR,
        '[data-testid-button-header="catalog"]'
    )

    city_locator = (
        By.XPATH,
        "//button[normalize-space(.)='Да, я здесь']"
    )

    with allure.step("Открыть сайт Читай-город"):
        driver.get(config["site_url"])

    with allure.step("Открыть каталог товаров"):
        catalog_button = wait.until(
            EC.element_to_be_clickable(catalog_locator)
        )

        try:
            catalog_button.click()

        except ElementClickInterceptedException:
            city_buttons = driver.find_elements(*city_locator)

            if not any(
                button.is_displayed() for button in city_buttons
            ):
                raise

            wait.until(
                EC.element_to_be_clickable(city_locator)
            ).click()

            wait.until(
                EC.invisibility_of_element_located(city_locator)
            )

            wait.until(
                EC.element_to_be_clickable(catalog_locator)
            ).click()

    with allure.step("Выбрать художественную литературу"):
        category_button = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//span[normalize-space()='Художественная литература']"
            ))
        )
        category_button.click()

    with allure.step("Нажать «Смотреть все товары»"):

        def find_category_link(
            browser: WebDriver
        ) -> WebElement | bool:
            links = browser.find_elements(
                By.CSS_SELECTOR,
                '[data-testid-link-catalog-menu="seeAll"]'
            )

            for link in links:
                parent = link.find_element(By.XPATH, "..")
                href = parent.get_attribute("href") or ""

                if (
                    "literatura-110001" in href
                    and parent.is_displayed()
                    and parent.is_enabled()
                ):
                    return parent

            return False

        see_all_link = wait.until(find_category_link)
        see_all_link.click()

    with allure.step("Дождаться страницы категории"):
        wait.until(
            EC.url_contains(
                "/catalog/books/hudozhestvennaya-literatura-110001"
            )
        )

    with allure.step("Убедиться, что открыта нужная категория"):
        category_heading = wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//h1[contains(., 'Художественная литература')]"
            ))
        )

        assert "Художественная литература" in category_heading.text
