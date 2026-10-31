
import json
import re
from pathlib import Path

import allure
import pytest
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
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


def get_visible_book_prices(
    driver: WebDriver,
) -> list[tuple[str | None, int]]:
    cards = driver.find_elements(
        By.CSS_SELECTOR,
        "article[data-testid-product-item]"
    )

    prices = []

    for card in cards:
        if not card.is_displayed():
            continue

        book_id = card.get_attribute(
            "data-testid-product-item"
        )
        book_price = get_book_price(card)

        prices.append((book_id, book_price))

    return prices


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
        previous_card = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "article[data-testid-product-item]")
            )
        )

        fields = WebDriverWait(driver, 15).until(
            get_price_fields
        )

        fields[1].send_keys(Keys.CONTROL, "a")
        fields[1].send_keys("1000")
        fields[1].send_keys(Keys.TAB)

    with allure.step("Дождаться обновления карточек товаров"):
        WebDriverWait(driver, 25).until(
            EC.staleness_of(previous_card)
        )

    with allure.step("Получить цены обновлённых карточек"):
        checked_prices = WebDriverWait(
            driver,
            30,
            ignored_exceptions=(
                StaleElementReferenceException,
                NoSuchElementException,
            ),
        ).until(get_visible_book_prices)

    with allure.step("Проверить цены книг в выдаче"):
        for book_id, book_price in checked_prices:
            assert 500 <= book_price <= 1000, (
                f"Книга ID {book_id}: цена {book_price} ₽ "
                "вне диапазона 500–1000 ₽"
            )

        assert checked_prices, "Не найдены цены книг"
