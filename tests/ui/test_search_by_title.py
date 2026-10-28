
import json
from pathlib import Path

import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.ui
@allure.title("UI-01 — Поиск книги по названию")
@allure.story("Поиск книг")
def test_search_by_title(driver: WebDriver) -> None:
    with allure.step("Загрузить настройки сайта"):
        config_path = Path(__file__).resolve().parents[2] / "config.json"
        config = json.loads(
            config_path.read_text(encoding="utf-8")
        )

    with allure.step("Открыть сайт Читай-город"):
        driver.get(config["site_url"])

    with allure.step("Найти поисковую строку"):
        search_input = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "app-search"))
        )

    with allure.step("Ввести название книги Гарри Поттер"):
        search_input.send_keys("Гарри Поттер")

        assert (
            search_input.get_attribute("value")
            == "Гарри Поттер"
        )
    with allure.step("Дождаться поисковых подсказок"):
        WebDriverWait(driver, 15).until(
            lambda browser: any(
                "гарри поттер" in item.text.casefold()
                for item in browser.find_elements(
                    By.CSS_SELECTOR,
                    'a[data-type="searchPhraseSuggest"]'
                )
            ),
            "Не появилась подсказка для запроса «Гарри Поттер»"
        )
    with allure.step("Нажать кнопку Найти"):
        search_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "form.search-form button[type='submit']"
                )
            )
        )

        search_button.click()

    with allure.step("Убедиться в переходе на страницу поиска"):
        WebDriverWait(driver, 15).until(
            EC.url_contains("/search/garri-potter")
        )

        assert "/search/garri-potter" in driver.current_url

    with allure.step("Убедиться, что найдена книга Гарри Поттер"):
        book_link = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "article[data-testid-product-item] a.product-card__title"
                )
            )
        )

        book_title = book_link.text.strip()

        assert "гарри поттер" in book_title.lower()
