import requests
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)


class NovaPoshtaService:
    API_URL = "https://api.novaposhta.ua/v2.0/json/"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_cities(self, city_name):
        """Отримує список міст для автодоповнення."""
        cache_key = f"nova_poshta_cities_{city_name}"
        cached_cities = cache.get(cache_key)
        if cached_cities:
            logger.debug(f"Повернуто з кешу для міста: {city_name}")
            return cached_cities

        payload = {
            "modelName": "Address",
            "calledMethod": "getCities",
            "methodProperties": {
                "FindByString": city_name,
                "Language": "ua"
            },
            "apiKey": self.api_key
        }

        logger.debug(f"Запит до API (getCities) з payload: {payload}")
        try:
            response = requests.post(self.API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Відповідь від API (getCities): {data}")

            if data.get('success'):
                cities = [
                    {'ref': c['Ref'], 'description': c['Description']}
                    for c in data['data']
                ]
                cache.set(cache_key, cities, timeout=3600)
                logger.debug(f"Знайдено {len(cities)} міст")
                return cities
            else:
                logger.error(f"Помилка API Нової"
                             f" Пошти (getCities): {data.get('errors')}")
                return []
        except requests.RequestException as e:
            logger.error(f"Помилка запиту до API Нової Пошти (getCities): {str(e)}")
            return []

    def get_warehouses(self, city_name):
        """Отримує список відділень для заданого міста."""
        cache_key = f"nova_poshta_warehouses_{city_name}"
        cached_warehouses = cache.get(cache_key)
        if cached_warehouses:
            logger.debug(f"Повернуто з кешу для міста: {city_name}")
            return cached_warehouses

        payload = {
            "modelName": "Address",
            "calledMethod": "getWarehouses",
            "methodProperties": {
                "CityName": city_name,
                "Language": "ua"
            },
            "apiKey": self.api_key
        }

        logger.debug(f"Запит до API з payload: {payload}")
        try:
            response = requests.post(self.API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Відповідь від API: {data}")

            if data.get('success'):
                warehouses = [
                    {'ref': w['Ref'], 'description': w['Description']}
                    for w in data['data']
                ]
                cache.set(cache_key, warehouses, timeout=3600)
                logger.debug(f"Знайдено {len(warehouses)} відділень")
                return warehouses
            else:
                logger.error(f"Помилка API Нової Пошти: {data.get('errors')}")
                return []
        except requests.RequestException as e:
            logger.error(f"Помилка запиту до API Нової Пошти: {str(e)}")
            return []
