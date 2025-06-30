import pytest
from unittest.mock import Mock, patch
from django.test import Client
from nova_poshta.services import NovaPoshtaService


@pytest.fixture
def nova_poshta_service():
    """Фікстура для створення сервісу Нової Пошти"""
    return NovaPoshtaService(api_key="test_api_key")


@pytest.fixture
def mock_api_response_cities():
    """Фікстура для мок відповіді API міст"""
    return {
        "success": True,
        "data": [
            {
                "Ref": "city_ref_1",
                "Description": "Київ"
            },
            {
                "Ref": "city_ref_2", 
                "Description": "Харків"
            }
        ]
    }


@pytest.fixture
def mock_api_response_warehouses():
    """Фікстура для мок відповіді API відділень"""
    return {
        "success": True,
        "data": [
            {
                "Ref": "warehouse_ref_1",
                "Description": "Відділення №1: вул. Тестова, 1"
            },
            {
                "Ref": "warehouse_ref_2",
                "Description": "Відділення №2: вул. Тестова, 2"
            }
        ]
    }


@pytest.fixture
def mock_api_error_response():
    """Фікстура для мок помилки API"""
    return {
        "success": False,
        "errors": ["API Error"]
    }


@pytest.fixture
def client():
    """Фікстура для Django test client"""
    return Client()
