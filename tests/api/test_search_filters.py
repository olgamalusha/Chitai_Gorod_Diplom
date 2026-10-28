
import json
from pathlib import Path

import allure
import pytest
import requests


@pytest.mark.api
@allure.title("API-01 — Получение поисковых фильтров")
@allure.story("Поиск книг")
def test_search_filters(guest_token: str) -> None:
    with allure.step("Загрузить настройки API"):
        config_path = Path(__file__).resolve().parents[2] / "config.json"
        config = json.loads(
            config_path.read_text(encoding="utf-8")
        )

    with allure.step("Отправить запрос поисковых фильтров"):
        url = f"{config['base_url']}/web/api/v2/search/facet-search"

        params = {
            "customerCityId": 213,
            "url": "garri-potter",
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

    with allure.step("Убедиться в успешном ответе API"):
        assert response.status_code == 200

    with allure.step("Убедиться, что список фильтров не пустой"):
        filters = response.json()["data"]

        assert isinstance(filters, list)
        assert len(filters) > 0
