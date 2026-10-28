
import json
from pathlib import Path

import allure
import pytest
import requests


@pytest.mark.api
@allure.title("API-03 — Поисковые подсказки по автору")
@allure.story("Поиск книг")
def test_search_author(guest_token: str) -> None:
    with allure.step("Загрузить настройки API"):
        config_path = Path(__file__).resolve().parents[2] / "config.json"
        config = json.loads(
            config_path.read_text(encoding="utf-8")
        )

    with allure.step("Отправить запрос с именем Стивен Кинг"):
        url = (
            f"{config['base_url']}"
            "/web/api/v2/search/search-phrase-suggests"
        )

        params = {
            "suggests[page]": 1,
            "suggests[per-page]": 5,
            "phrase": "стивен кинг",
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

    with allure.step("Получить список найденных авторов"):
        result = response.json()
        data = result["data"]

        assert isinstance(data, dict)

        authors = data["relationships"]["authors"]["data"]

        assert isinstance(authors, list)

    with allure.step("Убедиться, что найден хотя бы один автор"):
        assert len(authors) > 0

    with allure.step("Убедиться, что у автора есть ID"):
        first_author = authors[0]

        assert first_author["type"] == "searchFoundAuthor"
        assert first_author["id"]

    with allure.step("Убедиться, что найден автор Стивен Кинг"):
        included = result["included"]

        matching_authors = [
            item for item in included
            if item.get("id") == first_author["id"]
            and item.get("type") == first_author["type"]
        ]

        assert len(matching_authors) > 0

        assert (
            matching_authors[0]["attributes"]["fullName"]
            == "Стивен Кинг"
        )
