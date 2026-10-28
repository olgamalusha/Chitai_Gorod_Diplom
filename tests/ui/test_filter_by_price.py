
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait


def get_price_fields(driver: WebDriver) -> list[WebElement]:
    containers = driver.find_elements(
        By.CSS_SELECTOR,
        ".filter-range__input-wrapper"
    )

    for container in containers:
        if container.is_displayed():
            fields = container.find_elements(
                By.CSS_SELECTOR,
                "input.chg-app-input__control"
            )

            if len(fields) == 2:
                return fields

    return []


def get_book_price(card: WebElement) -> int:
    old_prices = card.find_elements(
        By.CSS_SELECTOR,
        ".product-mini-card-price__old-price"
    )

    if old_prices and old_prices[0].text.strip():
        price_text = old_prices[0].text
    else:
        price_text = card.find_element(
            By.CSS_SELECTOR,
            ".product-mini-card-price__price"
        ).text

    digits = re.sub(r"\D", "", price_text)
    assert digits, "Не удалось получить цену книги"

    return int(digits)


@pytest.mark.ui
@allure.title("UI-04 — Фильтрация книг по цене")
@allure.story("Фильтрация книг")
def test_filter_by_price(driver: WebDriver) -> None:
    config_path = Path(__file__).resolve().parents[2] / "config.json"
    config = json.loads(
        config_path.read_text(encoding="utf-8")
    )

    category_url = (
        config["site_url"]
        + "/catalog/books/hudozhestvennaya-literatura-110001"
    )

    with allure.step("Открыть художественную литературу"):
        driver.get(category_url)

    with allure.step("Установить минимальную цену 500 рублей"):
        fields = WebDriverWait(driver, 15).until(
            get_price_fields
        )

        fields[0].send_keys(Keys.CONTROL, "a")
        fields[0].send_keys("500")
        fields[0].send_keys(Keys.TAB)

    with allure.step("Установить максимальную цену 1000 рублей"):
        fields = WebDriverWait(driver, 15).until(
            get_price_fields
        )

        fields[1].send_keys(Keys.CONTROL, "a")
        fields[1].send_keys("1000")
        fields[1].send_keys(Keys.TAB)

    with allure.step("Дождаться применения диапазона в URL"):
        def filter_applied(browser: WebDriver) -> bool:
            params = parse_qs(urlparse(browser.current_url).query)

            return (
                params.get("filters[priceRetailMin]") == ["500"]
                and params.get("filters[priceRetailMax]") == ["1000"]
            )

        WebDriverWait(driver, 15).until(filter_applied)

    with allure.step("Обновить страницу с применённым фильтром"):
        driver.refresh()

        WebDriverWait(driver, 15).until(filter_applied)

    with allure.step("Проверить цены книг в выдаче"):
        cards = WebDriverWait(driver, 20).until(
            lambda browser: [
                card
                for card in browser.find_elements(
                    By.CSS_SELECTOR,
                    "article[data-testid-product-item]"
                )
                if card.is_displayed()
            ] or False
        )

        checked_prices = []

        for card in cards:
            book_price = get_book_price(card)
            checked_prices.append(book_price)

            book_id = card.get_attribute(
                "data-testid-product-item"
            )

            assert 500 <= book_price <= 1000, (
                f"Книга ID {book_id}: цена {book_price} ₽ "
                "вне диапазона 500–1000 ₽"
            )

        assert checked_prices, "Не найдены цены книг"
