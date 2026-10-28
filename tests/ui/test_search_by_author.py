
import json
from pathlib import Path

import allure
import pytest
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.ui
@allure.title("UI-02 — Поиск книг по автору")
@allure.story("Поиск книг")
def test_search_by_author(driver: WebDriver) -> None:
    config_path = Path(__file__).resolve().parents[2] / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    wait = WebDriverWait(driver, 15)

    with allure.step("Открыть сайт Читай-город"):
        driver.get(config["site_url"])

    with allure.step("Ввести имя автора и дождаться подсказки"):
        search_input = wait.until(
            EC.element_to_be_clickable((By.ID, "app-search"))
        )
        search_input.send_keys("Стивен Кинг")

        wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                'a[data-testid-suggest-link="стивен кинг"]'
            ))
        )

    with allure.step("Нажать кнопку поиска"):
        search_button = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "form.search-form button[type='submit']"
            ))
        )
        search_button.click()

    with allure.step("Дождаться страницы поиска"):
        wait.until(EC.url_contains("/search/stiven-king"))

    with allure.step("Убедиться, что найдены книги Стивена Кинга"):
        def author_found(browser: WebDriver) -> bool:
            authors = browser.find_elements(
                By.CSS_SELECTOR,
                "article[data-testid-product-item] "
                ".product-card__subtitle"
            )

            return any(
                "стивен кинг" in author.text.casefold()
                for author in authors
                if author.is_displayed()
            )

        WebDriverWait(
            driver,
            25,
            ignored_exceptions=(StaleElementReferenceException,)
        ).until(
            author_found,
            "В результатах поиска нет книг Стивена Кинга"
        )
