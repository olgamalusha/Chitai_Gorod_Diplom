
import json
from pathlib import Path

import allure
import pytest
import requests


@pytest.mark.api
@allure.title("API-04 — Запрос поисковых подсказок без авторизации")
@allure.story("Поиск книг")
def test_search_without_auth() -> None:
    with allure.step("Загрузить настройки API"):
        config_path = Path(__file__).resolve().parents[2] / "config.json"
        config = json.loads(
            config_path.read_text(encoding="utf-8")
        )

    with allure.step("Отправить запрос без токена авторизации"):
        url = (
            f"{config['base_url']}"
            "/web/api/v2/search/search-phrase-suggests"
        )

        params = {
            "suggests[page]": 1,
            "suggests[per-page]": 5,
            "phrase": "гарри поттер",
            "include": (
                "authors,bookCycles,categories,"
                "publishers,publisherSeries,products"
            ),
        }

        response = requests.get(
            url,
            params=params,
            timeout=15,
        )

    with allure.step("Убедиться, что сервер вернул статус 401"):
        assert response.status_code == 401

    with allure.step("Убедиться в сообщении об отсутствии авторизации"):
        assert (
            response.json()["message"]
            == "Authorization обязательное поле"
        )
