
import json
from pathlib import Path

import allure
import pytest
from selenium.common.exceptions import TimeoutException
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

    with allure.step("Найти книги автора Стивен Кинг"):
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

        search_button = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "form.search-form button[type='submit']"
            ))
        )
        search_button.click()

    with allure.step("Убедиться в переходе на страницу поиска"):

        try:
            wait.until(EC.url_contains("/search/stiven-king"))

        except TimeoutException:
            print("\n--- ДИАГНОСТИКА UI-02 ---")
            print("Текущий URL:", driver.current_url)
            print("Заголовок страницы:", driver.title)

            search_fields = driver.find_elements(By.ID, "app-search")
            if search_fields:
                print(
                    "Текст в поисковой строке:",
                    search_fields[0].get_attribute("value")
                )

            driver.save_screenshot("ui02_failure.png")
            print("Скриншот сохранён: ui02_failure.png")

            raise
