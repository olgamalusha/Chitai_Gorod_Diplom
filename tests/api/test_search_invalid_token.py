
import json
from pathlib import Path

import allure
import pytest
import requests


@pytest.mark.api
@allure.title("API-05 — Запрос с недействительным токеном")
@allure.story("Поиск книг")
def test_search_invalid_token() -> None:
    with allure.step("Загрузить настройки API"):
        config_path = Path(__file__).resolve().parents[2] / "config.json"
        config = json.loads(
            config_path.read_text(encoding="utf-8")
        )

    with allure.step("Подготовить недействительный токен"):
        headers = {
            "Authorization": "Bearer test.token",
        }

    with allure.step("Отправить запрос с недействительным токеном"):
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
            headers=headers,
            timeout=15,
        )

    with allure.step("Убедиться, что сервер вернул статус 401"):
        assert response.status_code == 401

    with allure.step("Убедиться в сообщении о неизвестном токене"):
        assert (
            response.json()["message"]
            == "JWTTokenMiddleware: token unknown"
        )
