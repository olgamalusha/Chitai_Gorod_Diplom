
import json
from pathlib import Path

import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.ui
@allure.title("UI-05 — Добавление книги в корзину")
@allure.story("Корзина")
def test_add_book_to_cart(driver: WebDriver) -> None:
    config_path = Path(__file__).resolve().parents[2] / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    book_url = (
        config["site_url"]
        + "/product/dve-krugosvetki-3026835"
    )

    wait = WebDriverWait(driver, 15)

    with allure.step("Открыть страницу книги «Две кругосветки»"):
        driver.get(book_url)

    with allure.step("Нажать кнопку «Купить»"):
        buy_button = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                '[data-testid-button-mini-product-card="canBuy"]'
            ))
        )
        buy_button.click()

    with allure.step("Убедиться, что появилась кнопка «Оформить»"):
        checkout_button = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                '[data-testid-button-mini-product-card="inCart"]'
            ))
        )

        assert checkout_button.text.strip() == "Оформить"

    with allure.step("Перейти в корзину"):
        checkout_button.click()

    with allure.step("Убедиться, что книга находится в корзине"):
        book_title = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                '[data-testid-text-cart-item="title"]'
            ))
        )

        assert book_title.text.strip() == "Две кругосветки", (
            f"В корзине отображается другая книга: {book_title.text}"
        )
