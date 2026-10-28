
import json
from pathlib import Path

import allure
import pytest
import requests


@pytest.mark.api
@allure.title("API-02 — Поисковые подсказки по названию книги")
@allure.story("Поиск книг")
def test_search_book(guest_token: str) -> None:
    with allure.step("Загрузить настройки API"):
        config_path = Path(__file__).resolve().parents[2] / "config.json"
        config = json.loads(
            config_path.read_text(encoding="utf-8")
        )

    with allure.step("Отправить запрос с фразой Гарри Поттер"):
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

        headers = {
            "Authorization": f"Bearer {guest_token}",
        }

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=15,
        )

    with allure.step("Убедиться, что сервер вернул статус 200"):
        assert response.status_code == 200

    with allure.step("Убедиться, что ответ содержит объект с ID"):
        result = response.json()
        data = result["data"]

        assert isinstance(data, dict)
        assert "id" in data
        assert data["id"] is not None

    with allure.step("Убедиться, что найдена подсказка Гарри Поттер"):
        included = result["included"]

        matching_suggestions = [
            item for item in included
            if item.get("type") == "searchPhraseSuggest"
            and item.get("attributes", {}).get("plainPhrase")
            == "гарри поттер"
        ]

        assert len(matching_suggestions) > 0
